from django.conf import settings

NAME_MAX_LENGTH = 128
UNIT_MAX_LENGTH = 64
DEFAULT_DATA_PATH = settings.BASE_DIR.parent / 'data' / 'ingredients.csv'
