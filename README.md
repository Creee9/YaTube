# Социальная сеть YaTube :iphone:

----------

### Стэк технологий:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)

----------

# Описание проекта

Cоциальную сеть для публикации личных дневников. Это сайт, на котором можно
создать свою страницу. Пользователи смогут заходить на чужие страницы,
подписываться на авторов, просматривать и
комментировать их записи.

### В проекте реализованы следующие функции:

* добавление/удаление постов авторизованными пользователями
* редактирование постов только его автором
* возможность авторизованным пользователям оставлять комментарии к постам
* подписка/отписка на понравившихся авторов
* создание отдельной ленты с постами авторов, на которых подписан пользователь
* создание отдельной ленты постов по группам(тематикам)
* Подключена пагинация, кеширование, авторизация пользователя
* возможна смена пароля через почту.
* Покрытие тестами.

----------

## Установка проекта*

###### *скопируйте содержимое поля снизу и запустите через командную строку.

```bash
# - Клонировать репозиторий:
git clone https://github.com/Creee9/YaTube.git

# - Cоздать и активировать виртуальное окружение:
python3 -m venv venv
source venv/script/activate

# - Установить зависимости из файла requirements.txt:
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# - перейти в папку "api_yamdb":
cd yatube/

# - Выполнить миграции:
python3 manage.py migrate

# - Запустить проект:
python3 manage.py runserver
```

###### *Ссылка на проект: [доступна по ссылке](http://localhost:8000/)
