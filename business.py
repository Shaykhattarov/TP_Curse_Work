import os
import json
import requests
import datetime

from flask_login import login_user
from app import config, db
from models import User, UserAuthorizationLog
from forms import ChangeUserForm, SelectUserForm


def __get_jsonfile_from_yandex(city: str):
    """ Получение json-файла с долготой и широтой в ответ на запрос """
    if not city:
        city = 'Ульяновск'

    try:
        response = requests.get(f'{config.YANDEX_API_GEOCODER_URL}?apikey={config.YANDEX_API_TOKEN}&geocode={city}&format=json')
        if response.status_code != 200:
            raise Exception(response.status_code)
    except Exception as err:
        return {
            'code': err,
            'data': 'Not Found!'
        }
    else:
        json_dir = os.path.join(f'{os.path.dirname(__file__)}', config.YANDEX_API_JSON)
        count_json = len(os.listdir(json_dir))
        with open(f'{json_dir}/result_{count_json}.json', 'w', encoding='utf-8') as file:
            file.write(response.text)
        dict_res = json.loads(response.content)
        position = dict_res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
        longitude = position[0]
        width = position[1]
        return {
            'code': response.status_code,
            'data': dict_res,
            'longitude': longitude,
            'width': width
        }


def __get_jpg_map_from_yandex(longitude, width):
    """ Получение изображения с картой города в ответ на запрос """
    if not longitude or not width:
        longitude = 48.384824
        width = 54.151718
    spn = [0.3, 0.3]
    size_w = 450
    size_h = 450
    scheme_l = 'map'
    url = f'{config.YANDEX_API_STATIC_MAP_URL}?apikey={config.YANDEX_API_TOKEN}&ll={longitude},{width}&' \
                              f'spn={spn[0]},{spn[1]}&size={size_w},{size_h}&l={scheme_l}'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(response.status_code)
    except Exception as err:
        return {
            'code': err,
            'data': 'Not Found!',
            'longitude': longitude,
            'width': width
        }
    else:
        img_dir = os.path.join(f'{os.path.dirname(__file__)}', config.YANDEX_API_IMG)
        count_img = len(os.listdir(img_dir))
        with open(f'{img_dir}/picture_{count_img}.jpg', 'wb') as file:
            file.write(response.content)
        return {
            'code': response.status_code,
            'img_name': f'picture_{count_img}.jpg'
        }


def view_yandex_data_on_main_page():
    """ Отображение последних запросов в Яндекс на главной странице """
    json_dir: str = os.path.join(os.path.dirname(__file__), config.YANDEX_API_JSON)

    count_img: int = len(os.listdir(os.path.join(os.path.dirname(__file__), config.YANDEX_API_IMG)))
    count_json: int = len(os.listdir(json_dir))

    last_json_dirpath: str = f'{json_dir}/result_{count_json - 1}.json'

    last_img_url_path: str = f'{config.YANDEX_API_IMG}/picture_{count_img - 1}.jpg'

    # Получаем данные из последнего сохраненного json-файла
    with open(last_json_dirpath, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

    # Страна последнего сохраненного запроса, федеральный округ, город
    country: str = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['description']
    federal_area: str = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData']['AddressDetails']['Country']["AdministrativeArea"]["AdministrativeAreaName"]
    city: str = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']

    return {
        'last_img_path': last_img_url_path,
        'country': country,
        'federal_area': federal_area,
        'city': city
    }


def view_yandex_data_by_response(city='Ульяновск'):
    """ Функция запрашивает данные у Яндекса и возвращает их """
    response_json_data = __get_jsonfile_from_yandex(city)

    # Забираем долготу и широту
    longitude = response_json_data['longitude']
    width = response_json_data['width']

    # Забираем json-данные, полученные из запроса
    json_data = response_json_data['data']

    # Парсим json-данные
    country = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['description']
    federal_area = \
        json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData'][
            'AddressDetails']['Country']["AdministrativeArea"]["AdministrativeAreaName"]
    city = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']

    # Запрашиваем и сохраняем карту, получаем ее filename
    img_name = __get_jpg_map_from_yandex(longitude, width)['img_name']
    img_url_path = f'{config.YANDEX_API_IMG}/{img_name}'

    return {
        'img_url_path': img_url_path,
        'country': country,
        'federal_area': federal_area,
        'city': city
    }


def change_user_profile(data: object, form: object):
    """ Эта функция сравнивает старые данные юзера с новыми из формы и изменяет старые """
    new_data = ChangeUserForm(
        name=form.name.data,
        surname=form.surname.data,
        email=form.email.data,
        password=form.password.data,
        confirm_password=form.confirm_password.data,
        work=form.work.data,
        old=form.old.data
    )

    changed_profile = User

    try:
        user = db.session.query(User).filter_by(id=data.id).one()
    except Exception as err:
        print(err)


    if new_data.name and new_data.name != data.name:
        changed_profile.name = new_data.name
    if new_data.surname and new_data.surname != data.surname:
        changed_profile.surname = new_data.surname
    if new_data.email and new_data.email != data.email:
        changed_profile.email = new_data.email
    if new_data.old and new_data.old != data.old:
        changed_profile.old = new_data.old
    if new_data.work and new_data.work != data.work:
        changed_profile.work = new_data.work

    if not User.check_password(user.password, new_data.password) and new_data.password == form.confirm_password.data:
        changed_profile.password = User.hash_password(new_data.password)

    try:
        db.session.add(changed_profile)
        db.session.commit()
    except Exception as err:
        print(err)
        return False

    return True


def authorization(login: str, password: str):
    """ В этой функции происходит авторизация пользователя """
    user = __get_user_by_email(login)
    if (user and user is not None) and (user.password is not None and User.check_password(user.password, password)):

        date_now = datetime.datetime.now()
        user_log = UserAuthorizationLog(user_id=user.id, username=user.name, date=date_now)

        # Логирование авторизаций
        try:
            db.session.add(user_log)
            db.session.commit()
        except Exception as err:
            print(err)

        return user
    else:
        return False


def __get_user_by_email(email):
    """ В этой функции происходит поиск пользователя с заданным email """
    try:
        user = db.session.query(User).filter(User.email == email).first()
    except Exception as err:
        print(err)
        return False
    else:
        if user is None:
            return None
        else:
            return user


def registration(form: object):
    """ В этой функции происходит регистрация пользователя """

    user = User(
        name=form.name.data,
        surname=form.surname.data,
        email=form.email.data,
        password=User.hash_password(form.password.data),
        old=form.old.data,
        work=form.work.data
    )

    try:
        # Поиск юзера с таким же email
        find_person = __get_user_by_email(user.email)

        if find_person is None:
            db.session.add(user)
            db.session.commit()
        else:
            raise Exception(find_person)
    except Exception as err:
        print(err)
        return False
    else:
        return True


def get_admin_profile_choice_list():
    """ В этой функции происходит формирование списка пользователей для редактирования Админом"""
    select_form = SelectUserForm()
    list_data = list()
    try:
        users = db.session.query(User).order_by(User.id).all()
    except Exception as err:
        print(err)
        return False
    else:
        for i in range(len(users)):
            list_data.append((str(users[i].id), users[i].email))

        select_form.id.default = ['3']
        select_form.id.choices = list_data

    return select_form


def get_selected_profile_by_admin(id: str):
    """ В этой функции идет формирование профиля юзера выбранного для редактирования Админом """
    try:
        user_response = db.session.query(User).filter(User.id == id).one()
    except Exception:
        return False
    else:
        if user_response is not None and user_response:
            user = User()
            user.id = user_response.id
            user.name = user_response.name
            user.surname = user_response.surname
            user.email = user_response.email
            user.old = user_response.old
            user.work = user_response.work

            return user
        else:
            return False


def change_selected_profile_by_admin(user: object, form: object):

    new_profile = ChangeUserForm(
        name=form.name.data,
        surname=form.surname.data,
        email=form.email.data,
        old=form.old.data,
        work=form.work.data
    )

    if new_profile.name and new_profile.name != user.name:
        user.name = new_profile.name
    if new_profile.surname and new_profile.surname != user.surname:
        user.surname = new_profile.surname
    if new_profile.email and new_profile.email != user.email:
        user.email = new_profile.email
    if new_profile.old and new_profile.old != user.old:
        user.old = new_profile.old
    if new_profile.work and new_profile.work != user.work:
        user.work = new_profile.work

    try:
        db.session.query(User).filter(User.id == id).update(user, synchronize_session=False)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return False
    else:
        return True








