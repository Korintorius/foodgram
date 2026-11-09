from django.conf import settings

NAME_MAX_LENGTH = 32
SLUG_MAX_LENGTH = 32
DEFAULT_DATA_PATH = settings.BASE_DIR.parent / 'data' / 'tags.csv'
