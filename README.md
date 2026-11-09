### Описание:

Описание: «Фудграм» — сайт, на котором пользователи смогут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Цель: Разработать backend приложения фудграм, выполнить deploy проекта на удаленный сервер. 

### Эмблема состояния рабочего процесса:
Будет добавлена в следующем релизе после реализации deploy

### Стек использованных технологий:
**Backend**
```
- asgiref 3.8.1
- attrs 24.2.0
- certifi 2024.12.14
- cffi 1.17.1
- charset-normalizer 3.4.1
- coreapi 2.3.3
- coreschema 0.0.4
- cryptography 44.0.0
- defusedxml 0.7.1
- Django 5.1.1
- django-templated-mail 1.1.1
- djangorestframework 3.15.2
- djangorestframework_simplejwt 5.4.0
- djoser 2.3.1
- flake8 7.1.1
- idna 3.10
- iniconfig 2.0.0
- itypes 1.2.0
- Jinja2 3.1.5
- MarkupSafe 3.0.2
- mccabe 0.7.0
- oauthlib 3.2.2
- packaging 24.2
- pillow 11.0.0
- pluggy 1.5.0
- py 1.11.0
- pycodestyle 2.12.1
- pycparser 2.22
- pyflakes 3.2.0
- PyJWT 2.10.1
- pyparsing 3.2.1
- pytest 8.3.3
- pytest-django 4.9.0
- pytest-pythonpath 0.7.3
- python3-openid 3.2.0
- pytz 2024.2
- requests 2.32.3
- requests-oauthlib 2.0.0
- six 1.17.0
- social-auth-app-django 5.4.2
- social-auth-core 4.5.4
- sqlparse 0.5.2
- toml 0.10.2
- uritemplate 4.1.1
- urllib3 2.3.0
- python-dotenv 1.2.4
- psycopg2-binary 2.9.11
- isort 9.0.2
```

**Базы данных и кэширование**
```
- PostgreSQL 13.10 - основная БД
- SQLite3 - временная БД 
```

**Инструменты и библиотеки**
```
- django.contrib.auth - Содержит необходимую функцию Django для получения активной модели пользователя.
- rest_framework - Ядро DRF для работы с сериализацией данных.
- rest_framework.filters - Модуль с готовыми классами для фильтрации queryset'ов.
- rest_framework.mixins - Набор готовых "примесей" (миксинов), реализующих базовые CRUD-действия.
- rest_framework.pagination - Класс для управления пагинацией
- rest_framework.permissions - Готовые классы для управления доступом к эндпоинтам
- rest_framework.viewset - Базовый класс для построения логики API через ViewSet'ы.
```

**Тестирование**
```
- pytest — тестирование
- pytest-django — интеграция с Django
```

### Установка:

**Клонировать репозиторий и перейти в него в командной строке:**

```
git clone https://github.com/Korintorius/foodgram.git
```

```
cd foodgram
```

**Cоздать и активировать виртуальное окружение:**

```
python3 -m venv env
```

```
source env/bin/activate
```

**Установить зависимости из файла requirements.txt:**

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

**Выполнить миграции:**

```
python3 manage.py migrate
```

**Запустить проект:**

```
python3 manage.py runserver
```

### Заполнение env.
POSTGRES_USER = логин пользователя для подключения к PostgreSQL
POSTGRES_PASSWORD = пароль для подключения
POSTGRES_DB =наименование базы данных

DB_HOST = db
DB_PORT = порт

DEBUG=true
SECRET_KEY = Код секретного ключа
ALLOWED_HOSTS=localhost,127.0.0.1,доменное имя при наличии
USE_SQLITE=false


### Автор: HAV.

**GitHub:**
```
https://github.com/Korintorius
```

**eMail:**
```
Korintorius@yandex.ru
```

