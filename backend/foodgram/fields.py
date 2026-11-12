import base64
import binascii

from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as lazy
from rest_framework import serializers

from foodgram.constants import DATA_URL_PATTERN


class Base64ImageField(serializers.ImageField):
    """Класс декодирования картинки."""

    default_error_message = {
        'invalid_base64': lazy('''Некорректное изображение: значение не
        декодируется как base64.'''),
        'empty_image': lazy('Изображение не должно быть пустым.'),
    }

    def to_internal_value(self, data):
        """Метод отправки на декодирование картинки в файл,
        если на входе строка."""
        if isinstance(data, str):
            data = self.decode_base64(data)
        return super().to_internal_value(data)

    def decode_base64(self, value):
        """Метод обработки самого изображения."""
        match = DATA_URL_PATTERN.match(value.strip())
        mime = (match.group('mime') if match else None) or 'image/png'
        payload = (match.group('payload') if match else value)
        payload = payload.replace('\n', '').replace('\r', '').strip()
        if ',' in payload:
            payload = payload.rsplit(',', 1)[-1]

        try:
            decoded = base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError):
            self.fail('invalid_base64')

        if not decoded:
            self.fail('empty_image')

        return ContentFile(
            decoded, name=f'image.{mime.split("/")[-1].lower() or "png"}')
