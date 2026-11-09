import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ingredients.constants import (
    DEFAULT_DATA_PATH,
    NAME_MAX_LENGTH,
    UNIT_MAX_LENGTH)
from ingredients.models import Ingredient


class Command(BaseCommand):
    """Загрузка справочника ингредиентов из data/ingredients.json или .csv."""

    def add_arguments(self, parser):
        """Метод, описывающий параметры для запуска."""
        parser.add_argument(
            '--path',
            type=Path,
            default=DEFAULT_DATA_PATH,
            help="""Путь к файлу с ингредиентами
            (по умолчанию data/ingredients.json)."""
        )

        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Размер пачки для bulk_create (по умолчанию 500)',
        )

    def handle(self, *args, **options):
        """Метод основного сценария чтения, проверки и
        создания новых записей."""
        path = options['path']
        if not path.exists():
            raise CommandError(f'Файл с данными не найден: {path}')

        rows = self.read_rows(path)
        self.validate_rows(rows)

        existing_names = set(Ingredient.objects.values_list('name', flat=True))
        new_rows = [
            row for row in rows
            if row['name'] not in existing_names
        ]
        duplicates = len(rows) - len({row['name'] for row in rows})

        created = Ingredient.objects.bulk_create(
            [Ingredient(**row) for row in new_rows],
            batch_size=options['batch_size'],)

        self.stdout.write(self.style.SUCCESS(
            f'Создано ингредиентов: {len(created)};'
            f'пропущено (уже в базе): {len(rows) - len(new_rows)};'
            f'дублей внутри файла: {duplicates}'
        ))

    def read_rows(self, path: Path) -> list[dict[str, str]]:
        """Метод чтения файла. (csv/json)."""
        suffix = path.suffix.lower()

        if suffix == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as file:
                reader = csv.reader(file)
                return [
                    {'name': row[0].strip(),
                     'measurement_unit': row[1].strip()}
                    for row in reader
                    if len(row) >= 2 and row[0].strip()
                ]

        if suffix == '.json':
            with path.open(encoding='utf-8') as file:
                raw = json.load(file)
            if not isinstance(raw, list):
                raise ValueError(f"Ожидался JSON-массив в {path}")
            return [
                {
                    'name': str(item['name']).strip(),
                    'measurement_unit': str(item['measurement_unit']).strip(),
                }
                for item in raw
                if item.get('name') is not None
                and item.get('measurement_unit') is not None
            ]

        raise ValueError(f"Неподдерживаемый формат файла: {suffix}")

    def validate_rows(self, rows):
        """Метод валидации данных."""
        errors = []
        for index, row in enumerate(rows, start=1):
            name = row['name']
            unit = row['measurement_unit']

            if not name:
                errors.append(f'строка {index}: не указано название')
            elif len(name) > NAME_MAX_LENGTH:
                errors.append(
                    f'строка {index}: название длиннее'
                    f'{NAME_MAX_LENGTH} символов'
                )

            if not unit:
                errors.append(f'строка {index}: не указана единица измерени')
            elif len(unit) > UNIT_MAX_LENGTH:
                errors.append(
                    f'строка {index}: единица измерения длиннее'
                    f'{UNIT_MAX_LENGTH} символов'
                )

        if errors:
            preview = '\n'.join(errors[:10])
            raise CommandError(f'Данные некорректны:\n{preview}')
