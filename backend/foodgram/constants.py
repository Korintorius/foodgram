import re

DATA_URL_PATTERN = re.compile(
    r'^data:(?P<mime>[\w.+-]+/[\w.+-]+)?'
    r'(?P<parameters>;[^,]*)?,'
    r'(?P<payload>.*)$',
    re.DOTALL,)
