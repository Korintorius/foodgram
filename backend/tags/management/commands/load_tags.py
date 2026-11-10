import csv
import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_slug

from tags.constants import DEFAULT_DATA_PATH, NAME_MAX_LENGTH, SLUG_MAX_LENGTH
from tags.models import Tag


class Command(BaseCommand):
    """Загрузка справочника тегов из data/tags.json или .csv в БД."""

    def add_arguments(self, parser):
        """Добавляет параметры для:
        - --path,
        - --batch-size.
        """
        parser.add_argument(
            '--path',
            type=Path,
            default=DEFAULT_DATA_PATH,
            help=f'Путь к файлу с тегами (по умолчанию {DEFAULT_DATA_PATH}).',
        )

        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Размер пачки для bulk_create (по умолчанию 100)',
        )

    def handle(self, *args, **options):
        """Чтение, проверка и сохранения тегов, которых еще не было."""
        path = options['path']
        if not path.exists():
            raise CommandError(f'Файл с данными не найден: {path}')

        batch_size = options['batch_size']
        if batch_size <= 0:
            raise CommandError('--batch-size должен быть больше 0')

        rows = self.read_rows(path)
        self.validate_rows(rows)

        new_rows, skipped_existing, skipped_duplicates = (
            self.filter_new_rows(rows)
        )

        created = Tag.objects.bulk_create(
            [Tag(**row) for row in new_rows],
            batch_size=options['batch_size'],
        )

        self.stdout.write(self.style.SUCCESS(
            f'Создано тегов: {len(created)};'
            f'пропущено (уже в базе): {skipped_existing};'
            f'дублей внутри файла: {skipped_duplicates}'
        ))

    def read_rows(self, path: Path) -> list[dict[str, str]]:
        """Чтение CSV или JSON."""
        suffix = path.suffix.lower()

        if suffix == '.csv':
            return self.read_csv_rows(path)
        if suffix == '.json':
            return self.read_json_rows(path)

        extension = suffix or '<без расширения>'
        raise CommandError(f'Неподдерживаемый формат файла: {extension}')

    def read_csv_rows(self, path: Path) -> list[dict[str, str]]:
        """Четение тегов из CSV-файла."""
        with path.open(encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = set(reader.fieldnames or [])
            missing = {'name', 'slug'} - fieldnames

            if missing:
                raise CommandError(
                    f'В файле {path} отсутствуют колонки: '
                    f'{", ".join(sorted(missing))}'
                )

            rows = []
            for raw in reader:
                name = (raw.get('name') or '').strip()
                slug = (raw.get('slug') or '').strip()

                if not name and not slug:
                    continue

                rows.append({'name': name, 'slug': slug})

        return rows

    def read_json_rows(self, path: Path) -> list[dict[str, str]]:
        """Четение тегов из JSON-файла."""
        try:
            with path.open(encoding='utf-8-sig') as file:
                raw = json.load(file)
        except json.JSONDecodeError as error:
            raise CommandError(
                f'Не удалось прочитать JSON из {path}: {error}'
            ) from error

        if not isinstance(raw, list):
            raise CommandError(f'Ожидался JSON-массив в {path}')

        rows = []
        for index, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                raise CommandError(
                    f'Элемент {index} в {path} не является объектом'
                )

            name = item.get('name')
            slug = item.get('slug')

            if name is None or slug is None:
                raise CommandError(
                    f'Элемент {index} в {path}: '
                    'отсутствует поле name или slug'
                )
            rows.append({
                'name': str(name).strip(),
                'slug': str(slug).strip(),
            })
        return rows

    def validate_rows(self, rows: list[dict[str, str]]) -> None:
        """Проверка обязательности поля, длины и формата слага."""
        errors = []

        for index, row in enumerate(rows, start=1):
            name = row['name']
            slug = row['slug']

            if not name:
                errors.append(f'строка {index}: не указано название')
            elif len(name) > NAME_MAX_LENGTH:
                errors.append(
                    f'строка {index}: название длиннее '
                    f'{NAME_MAX_LENGTH} символов'
                )

            if not slug:
                errors.append(f'строка {index}: не указан слаг')
            elif len(slug) > SLUG_MAX_LENGTH:
                errors.append(
                    f'строка {index}: слаг длиннее '
                    f'{SLUG_MAX_LENGTH} символов'
                )
            else:
                try:
                    validate_slug(slug)
                except ValidationError:
                    errors.append(
                        f'строка {index}: недопустимый слаг {slug!r}'
                    )

        if not errors:
            return
        preview = '\n'.join(errors[:10])
        if len(errors) > 10:
            preview += f'\n... и еще {len(errors) - 10} ошибок'
        raise CommandError(f'Данные некорректны:\n{preview}')

    def filter_new_rows(self, rows):
        """Отбрасывает существующие теги и дубли внутри файла."""
        existing_names = set(
            Tag.objects.values_list('name', flat=True)
        )
        existing_slugs = set(
            Tag.objects.values_list('slug', flat=True)
        )

        new_rows = []
        seen_names = set()
        seen_slugs = set()
        skipped_existing = 0
        skipped_duplicates = 0

        for row in rows:
            name = row['name']
            slug = row['slug']

            if name in existing_names or slug in existing_slugs:
                skipped_existing += 1
                continue

            if name in seen_names or slug in seen_slugs:
                skipped_duplicates += 1
                continue

            new_rows.append(row)
            seen_names.add(name)
            seen_slugs.add(slug)
        return new_rows, skipped_existing, skipped_duplicates
