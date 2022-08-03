# Ditexos

###### Автоматизация отчетности.
###### Проект собирает метрики с рекламных кабинетов и CRM систем и на основе полученных данных данных строит различные виды отчетов.
###### Параметризация и просмотр отчетов организовано в веб интерфейсе, также существует возможность генерировать Excel файлы.

## Реализована поддержка систем:
 - Yandex direct
 - Google ads
 - VK ads
 - Mytarget
 - AmoCRM
 
 # Инсталляция
 
 ## SSL Сертифкаты.
 Создать каталог /etc/ssl и добавить туда сертификаты *.crt, *.key.
 
 ## Переменные окружения.
Создать файл c переменными окружения .env в каталоге */ditexos/ditexos.
 
Содержимое файла:
```
DEBUG=принимает значение True или False, в продакт выставить значение False
SECRET_KEY=Секретный ключ джанго
DB_NAME=db_name
DB_USER=user
DB_PASSWORD=password
DB_HOST=127.0.0.1
DB_PORT=5432
BROKER_URL=amqp://user:password@127.0.0.1:5675/

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

GOOGLE_DEVELOPER_TOKEN=токен разработчика Google Ads
GOOGLE_APP_ID=Идентификатор приложения OAuth 2.0 Client IDs
GOOGLE_PROJECT_ID=Идентификатор проекта
GOOGLE_APP_PASSWORD=Client secret OAuth 2.0 Client IDs
GOOGLE_REDIRECT_URIS=['url',]
GOOGLE_REDIRECT_URI=url

GOOGLE_SHEETS_APP_ID=Идентификатор проекта
GOOGLE_SHEETS_PROJECT_ID=Идентификатор приложения OAuth 2.0 Client IDs
GOOGLE_SHEETS_APP_PASSWORD=Client secret OAuth 2.0 Client IDs
GOOGLE_SHEETS_REDIRECT_URIS=['url',]
GOOGLE_SHEETS_REDIRECT_URI=url

YANDEX_APP_ID=Идентификатор приложения OAuth 2.0
YANDEX_APP_PASSWORD=Client secret
YANDEX_REDIRECT_URI=url

VK_APP_ID=Идентификатор приложения OAuth 2.0
VK_APP_SECRET=Client secret
VK_REDIRECT_URI=url

AMO_REDIRECT_URI=url

EMAIL_HOST=smtp.xxxx.ru
EMAIL_PORT=465
EMAIL_HOST_USER=user@user.ru
DEFAULT_FROM_EMAIL=user@user.ru
EMAIL_HOST_PASSWORD=password
```
 
Сбор контейнеров:
 ```
 docker-compose build
 ```
 
 Запуск контейнеров:
 ```
 docker-compose up
 ```
 
# Кастомные команды manage.py:
##### Создание первого пользователя с правами суперюзера:
###### Необходимо для автоматической развертки в контейнере.
```
python manage.py create_first_user
```
##### Создание sql views:
```
python manage.py create_views
```


# В проекте использовались технологии:
- Django
- Celery
- Bootstrap4

[Телеграм автора проекта](https://t.me/maxim_mnm)
