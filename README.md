# Foodgram
Foodgram (Продуктовый помощник) - онлайн сервис. На данном сайте пользователи могут просматривать рецепты других пользователей, публиковать свои рецепты, подписываться на интересующих их авторов, добавлять понравившиеся рецепты в избранное и в список покупок, а также скачивать список покупок с требуемыми ингредиентами для приготовления блюд.
## Адрес сайта: http://frolovfoodgram.ddns.net/
## Аккаунт суперюзера:
##### login(email): a@a.ru
##### password: AdminPass1

## Запуск проекта:
Клонируйте репозиторий:
```
git@github.com:We1der/foodgram-project-react.git
```
Установите Docker и Docker compose:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
Создайте файл .env и запишите там следующие данные:
`POSTGRES_DB` - имя базы данных
`POSTGRES_USER` - имя пользователя для БД
`POSTGRES_PASSWORD` - пароль для БД
`DB_HOST` - имя хоста БД
`DB_PORT` - порт БД
`SECRET_KEY` - секретный ключ от django
`DB` - название нужной БД (POSTGRES/SQLITE)
`DEBUG` - отладка django (True\False)

Скопируйте файлы docker-compose.yml, nginx.conf из папки infra:
```
scp docker-compose.yml nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

Запустите проект, находясь в infra, командой:
```
sudo docker compose -f docker-compose.yml up -d
```

### Author
Mikhail Frolov