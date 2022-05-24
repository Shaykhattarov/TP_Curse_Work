import datetime
import os

from app import app, db, login_manager
from forms import ChangeUserForm, LoginForm, CreateUserForm, SelectUserForm, CreateNewsForm, SelectNewsForm, \
    ChangeNewsForm
from models import User, News, Category, NewsCreatingLog

from business import view_yandex_data_on_main_page, view_yandex_data_by_response, get_selected_profile_by_admin, \
    change_selected_profile_by_admin
from business import authorization, registration, change_user_profile
from business import get_admin_profile_choice_list

from flask import render_template, flash, redirect, request, url_for, jsonify, abort
from flask_login import login_required, login_user, current_user, logout_user


@app.route('/')
@app.route('/home')
def index():
    """ Здесь происходит отрисовка Главной страницы """
    last_response = view_yandex_data_on_main_page()
    return render_template('index.html', img=last_response['last_img_path'], country=last_response['country'],
                           federal_area=last_response['federal_area'], city=last_response['city'])


@app.route('/city-map/<string:city>')
def city_map(city):
    """ Здесь происходит работа с Яндекс.API """
    response_data = view_yandex_data_by_response(city)
    return render_template('search.html', img=response_data['img_url_path'], country=response_data['country'],
                           federal_area=response_data['federal_area'], city=response_data['city'])


@app.route('/profile/', methods=['get', 'post'])
@login_required
def profile():
    """ Здесь проходит работа страницы профиля пользователя """
    if not current_user.is_authenticated:
        return redirect('login')
    form = ChangeUserForm()
    message = ""
    if request.method == 'POST':
        data = dict({
            'name': current_user.name,
            'surname': current_user.surname,
            'login': current_user.email,
            'password': current_user.password,
            'old': current_user.old,
            'work': current_user.work
        })

        new_data = dict({
            'name': form.name.data,
            'surname': form.surname.data,
            'login': form.email.data,
            'password': form.password.data,
            'confirm_password': form.confirm_password.data,
            'old': form.old.data,
            'work': form.work.data
        })

        user = db.session.query(User).filter_by(id=current_user.id).one()
        if new_data['name'] and new_data['name'] != data['name']:
            data['name'] = new_data['name']
        if new_data['surname'] and new_data['surname'] != data['surname']:
            data['surname'] = new_data['name']
        if new_data['login'] and new_data['login'] != data['login']:
            data['login'] = new_data['login']
        if new_data['old'] and new_data['old'] != data['old']:
            data['old'] = new_data['old']
        if new_data['work'] and new_data['work'] != data['work']:
            data['work'] = new_data['work']
        if not User.check_password(data['password'], new_data['password']) and new_data['password'] == new_data[
            'confirm_password']:
            data['password'] = User.hash_password(new_data['password'])

        user.name = data['name']
        user.surname = data['surname']
        user.email = data['login']
        user.password = data['password']
        user.old = data['old']
        user.work = data['work']

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            message = "Изменение данных в бд прошло с ошибкой!"
            print(e)
        else:
            current_user.name = data['name']
            current_user.surname = data['surname']
            current_user.email = data['login']
            current_user.password = data['password']
            current_user.old = data['old']
            current_user.work = data['work']
            return redirect(url_for('profile'))

    return render_template('profile.html', form=form, message=message)


@app.route('/login/', methods=['post', 'get'])
def login():
    """ Здесь происходит авторизация пользователя """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'POST':
        auth_result = authorization(login=form.email.data, password=form.password.data)

        if auth_result:
            login_user(auth_result)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('auth_form.html', form=form)


@login_manager.user_loader
def load_user(id):
    return db.session.query(User).get(id)


@app.route('/reg/', methods=['post', 'get'])
def registration():
    """ Здесь происходит регистрация пользователя """
    form = CreateUserForm()

    if form.validate_on_submit():
        registration_result = registration(form)

        if registration_result:
            return redirect(url_for('login'))
        else:
            return redirect(url_for('registration'))
    return render_template('reg_form.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin-choice/', methods=['get', 'post'])
def admin_choice():
    """ Здесь выводиться список пользователей для редактирования пользователем Админом"""
    if current_user.email != "admin@admin.ru" and current_user.password != "admin":
        return redirect(url_for('registration'))

    choice_list_area = get_admin_profile_choice_list()

    if request.method == "POST":
        id = int(choice_list_area.id.data[0])
        return redirect(url_for('admin', user_id=id))

    return render_template('admin_choice_form.html', select_form=choice_list_area)


@app.route('/admin/', methods=['get', 'post'])
@login_required
def admin():
    if current_user.email != "admin@admin.ru" and current_user.password != "admin":
        return redirect(url_for('registration'))
    id = request.args.get('user_id')
    form = ChangeUserForm()
    message = ""
    try:
        user_response = db.session.query(User).filter(User.id == id).one()
    except Exception as e:
        print(e)
    else:
        user_info = User()
        user_info.id = user_response.id
        user_info.name = user_response.name
        user_info.surname = user_response.surname
        user_info.email = user_response.email
        user_info.old = user_response.old
        user_info.work = user_response.work

    if request.method == 'POST':
        data = dict({
            'name': user_info.name,
            'surname': user_info.surname,
            'login': user_info.email,
            'old': user_info.old,
            'work': user_info.work
        })
        new_data = dict({
            'name': form.name.data,
            'surname': form.surname.data,
            'login': form.email.data,
            'old': form.old.data,
            'work': form.work.data
        })

        if new_data['name'] and new_data['name'] != data['name']:
            data['name'] = new_data['name']
        if new_data['surname'] and new_data['surname'] != data['surname']:
            data['surname'] = new_data['surname']
        if new_data['login'] and new_data['login'] != data['login']:
            data['login'] = new_data['login']
        if new_data['old'] and new_data['old'] != data['old']:
            data['old'] = new_data['old']
        if new_data['work'] and new_data['work'] != data['work']:
            data['work'] = new_data['work']

        try:
            update_query = db.session.query(User).filter(User.id == id).update(
                {User.name: data['name'], User.surname: data['surname'], User.email: data['login'],
                 User.old: data['old'], User.work: data['work']}, synchronize_session=False)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            message = "Изменение данных в бд прошло с ошибкой!"
            print(e)
        else:
            return redirect(url_for('admin', user_id=id))

    return render_template('admin.html', form=form, data=user_info, message=message)


@app.route('/news/', methods=['get', 'post'])
@app.route('/news/<int:page>', methods=['get', 'post'])
def news(page=1):
    news = list()
    posts = str()

    try:
        posts = db.session.query(News, Category.name).join(Category).filter(News.title != None).order_by(News.date).paginate(page, app.config['POSTS_PER_PAGE'], False)
    except Exception as err:
        print(err)

    return render_template('news.html', posts=posts)


@app.route('/author/', methods=['get', 'post'])
@app.route('/author/<author>/', methods=['get', 'post'])
@app.route('/author/<author>', methods=['get', 'post'])
@app.route('/author/<author>/<int:page>', methods=['get', 'post'])
def user_news(author, page=1):
    posts = str()

    try:
        posts = db.session.query(News, Category.name).join(Category).filter(News.author == author).filter(News.title != None).order_by(News.date).paginate(page, app.config['POSTS_PER_PAGE'], False)
    except Exception as err:
        print(err)

    return render_template('news.html', posts=posts)


@app.route('/category', methods=['get', 'post'])
@app.route('/category/<category>', methods=['get', 'post'])
@app.route('/category/<category>/', methods=['get', 'post'])
@app.route('/category/<category>/<int:page>', methods=['get', 'post'])
def category_news(category, page=1):
    posts = list()

    try:
        posts = db.session.query(News, Category.name).join(Category).filter(News.title != None).filter(Category.name == category).order_by(News.date).paginate(page, app.config["POSTS_PER_PAGE"], False)
    except Exception as err:
        print(err)
    else:
        if not posts.items or len(posts.items) == 0:
            redirect(url_for('news'))

    return render_template('news.html', posts=posts)


@app.route('/create-news/', methods = ['get', 'post'])
@login_required
def create_news():
    form = CreateNewsForm()
    post = News()
    category_list = list()
    message = ''

    try:
        categories = db.session.query(Category).order_by(Category.id).all()
        for category in categories:
            category_list.append((str(category.id), category.name))
        form.category.default = ['1']
        form.category.choices = category_list
    except Exception as err:
        message = "Произошла ошибка!"
        print(f'Ошибка: {err}')

    if request.method == "POST":
        image_url = str()
        file_url = str()

        post.user_id = current_user.id
        post.title = form.title.data
        post.intro = form.intro.data
        post.text = form.text.data
        post.category_id = int(form.category.data[0])
        post.author = current_user.name
        post.date = datetime.datetime.today()

        if form.img.data:
            image = form.img.data
            image_url = os.path.join(app.config['UPLOADED_NEWS_PHOTO'], image.filename)
            image.save(image_url)
            post.img = f'/data/news_img/{image.filename}'
        if form.file.data:
            file = form.file.data
            file_url = os.path.join(app.config['UPLOADED_NEWS_FILE'], file.filename)
            file.save(file_url)
            post.file = f'/data/news_files/{file.filename}'
        else:
            file_url = None

        if post.title and post.title != None:
            try:
                db.session.add(post)
                db.session.commit()
            except Exception as err:
                message = "Произошла ошибка!"
                print(err)
            else:
                message = "Пост создан!"
                news_log = NewsCreatingLog(author_id=post.user_id, author_name=post.author, news_title=post.title, date=datetime.datetime.now())
                try:
                    db.session.add(news_log)
                    db.session.commit()
                except Exception as err:
                    print(err)

    return render_template('create_news.html', form=form, message=message)


@app.route('/select-change-post/', methods=['get', 'post'])
@login_required
def select_change_post():
    if current_user.email != "admin@admin.ru" and current_user.password != "admin":
        return redirect(url_for('index'))

    form = SelectNewsForm()
    posts = list()

    try:
        response = db.session.query(News).filter(News.title != None).order_by(News.date).all()
        for post in response:
            posts.append((str(post.id), post.title))
        form.post.default = ['1']
        form.post.choices = posts
    except Exception as err:
        print(err)
    else:
        if request.method == "POST":
            post_id = int(form.post.data[0])
            return redirect(url_for('change_news', post_id=str(post_id)))

    return render_template('admin_choice_news_form.html', form=form)


@app.route('/change-news/', methods = ['get', 'post' ])
def change_news():
    if current_user.email != "admin@admin.ru" and current_user.password != "admin":
        return redirect(url_for('index'))
    post_id = request.args.get('post_id')
    form = ChangeNewsForm()
    category_list = list()
    try:
        post = db.session.query(News, Category.name).join(Category).filter(News.title != None).filter(News.id == post_id).order_by(News.date).first()
        categories = db.session.query(Category).order_by(Category.id).all()
        for category in categories:
            category_list.append((str(category.id), category.name))
        form.category.default = ['1']
        form.category.choices = category_list
    except Exception as err:
        print(err)
    else:
        if request.method == "POST":
            new_category = int(form.category.data[0])

            try:
                update_query = db.session.query(News).filter(News.id == post_id).update(
                    {News.category_id: new_category}, synchronize_session=False)
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                print(err)
            else:
                return redirect(url_for('select_change_post'))

    return render_template('change_news.html', post=post, form=form)


@app.route('/api/news', methods = ['GET'])
def get_all_news():
    domen = 'http://127.0.0.1:5000'
    posts = list()
    try:
        posts = db.session.query(News, Category.name).join(Category).filter(News.title != None).order_by(
            News.date).all()
    except Exception as err:
        print(err)
        abort(404)
    else:
        news_list = list()
        news_lis = list()
        for post, category in posts:
            news_list.append({
                'title': post.title,
                'intro': post.intro,
                'text': post.text,
                'author': post.author,
                'img': f'{domen}/static{post.img}',
                'file_url': f'{domen}/static{post.file}',
                'date': post.date,
                'category': category
            })
        if len(news_list) == 0:
            abort(404)
    return jsonify({ 'news' : news_list}), 200


@app.route('/api/news/category/<string:category>')
def get_category_news(category):
    domen = 'http://127.0.0.1:5000'
    posts = list()
    try:
        posts = db.session.query(News, Category.name).join(Category).filter(News.title != None).filter(
            Category.name == category).order_by(News.date).all()
    except Exception as err:
        abort(404)
    else:
        news_list = list()
        news_lis = list()
        for post, category in posts:
            news_list.append({
                'title': post.title,
                'intro': post.intro,
                'text': post.text,
                'author': post.author,
                'img': f'{domen}/static{post.img}',
                'file_url': f'{domen}/static{post.file}',
                'date': post.date,
                'category': category
            })

        if len(news_list) == 0:
            abort(404)

    return jsonify({'news': news_list})


# Обработчик ошибок
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not Found!'}), 404
    else:
        return render_template('404.html'), 404