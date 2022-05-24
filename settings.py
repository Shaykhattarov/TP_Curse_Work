import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SECRET_KEY = ' AAAAB3NzaC1yc2EAAAADAQABAAABgQDjpNwz5lbIEPRWw2RRzsZAJNmXInOGmDsUFDRDTo7cPdLQrD7jHzgogAYh0PIxvmAnTBAUg77+' \
                 'lCaL3EifSfi7gd4dOnv+L2b07eVra7VuYw9cQ2amYQdpTs3bZU9k9vbDXCgZPR0xrOifrg3x2P8vZs9lHrhUhWYA70pd3ouXhV1ljftmbVqAF6Jmll' \
                 'dCGgvPgMimMukCv/jXno2lfgi/ZSzidwngow5Ecv1jSgZja3GpO2DLf0Jyr3WcO+15/i6tHHHJf88ZJIV8sGm7m4NWE50i7Ab+eDOsgJbZyjfgyCUFJQQg' \
                 'siOpjGVYm6LrtZx5a8gGnp0MHPzYdMo+7P9w0I1fv9dShcfi/kz1ekadyHjr/B+EOkfItOH7Dslzrnilp7VLyA61nKcftGy9lJOF8rn2v43kBQNDSQGvcjlUd' \
                 'cFJ3t6ANG3s3zBzpFCbUoniAGtP8hbt74wqL8Qvaw+wgB8e/7hZeobeS+gdkVf1uAkuPalHJlp46XKRTA5ZqyE='


    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'database/app.db') + '?charset=utf-8'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    YANDEX_API_GEOCODER_URL = 'https://geocode-maps.yandex.ru/1.x/'
    YANDEX_API_STATIC_MAP_URL = 'http://static-maps.yandex.ru/1.x/'

    YANDEX_API_TOKEN = 'abf6ba70-553c-4715-b061-ffe5618e5702'
    YANDEX_API_JSON = f'static/data/json_api'
    YANDEX_API_IMG = f'static/data/pictures_api'

    RENDER_AS_BATCH = True

    POSTS_PER_PAGE = 3

    UPLOADED_NEWS_PHOTO = os.path.join(basedir, 'static/data/news_img')
    UPLOADED_NEWS_FILE = os.path.join(basedir, 'static/data/news_files')

    JSON_AS_ASCII = False

    HOST = '0.0.0.0'
    PORT = '8000'
