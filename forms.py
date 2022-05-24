from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectMultipleField, FileField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = EmailField(label=("Электронная почта"), validators=[InputRequired(), Email(), Length(max=2025)])
    password = PasswordField(label=('Пароль'), validators=[InputRequired(), Length(min=5, message='Password should be at least %(min)d characters long')])
    submit = SubmitField(label=('Авторизоваться'))


class CreateUserForm(FlaskForm):
    name = StringField(label=('Имя'), validators=[DataRequired(), Length(max=120)])
    surname = StringField(label=('Фамилия'), validators=[DataRequired(), Length(max=120)])
    email = EmailField(label=('Электронная почта'), validators=[DataRequired(), Email(), Length(max=2025)])
    password = PasswordField(label=('Пароль'), validators=[InputRequired()])
    old = StringField(label=('Возраст'), validators=[DataRequired(), Length(max=120)])
    work = StringField(label=('Должность и работа'), validators=[DataRequired(), Length(max=120)])
    photo = ""
    submit = SubmitField(label=('Зарегистрироваться'))


class ChangeUserForm(FlaskForm):
    name = StringField(label=('Имя'), validators=[Length(max=120)])
    surname = StringField(label=('Фамилия'), validators=[Length(max=120)])
    email = EmailField(label=('Электронная почта'), validators=[Email(), Length(max=2025)])
    password = PasswordField(label=('Пароль'), validators=[])
    confirm_password = PasswordField(label=('Подтверждение пароля'), validators=[])
    old = StringField(label=('Возраст'), validators=[Length(max=120)])
    work = StringField(label=('Должность и работа'), validators=[Length(max=120)])
    photo = ""
    submit = SubmitField(label=('Подтвердить изменения'))


class SelectUserForm(FlaskForm):
    id = SelectMultipleField(label=('ID'), validators=[Length(max=120000)])
    submit = SubmitField(label=('Выбрать пользователя'))


class CreateNewsForm(FlaskForm):
    title = StringField(label=('Заголовок поста'), validators=[InputRequired(), DataRequired(), Length(min=6, max=255)])
    intro = StringField(label=('Вступительный текст поста'), validators=[InputRequired(), DataRequired(), Length(max=1000)])
    category = SelectMultipleField(label=('Категория'), validators=[InputRequired(), DataRequired()])
    img = FileField(label=('Изображение поста'), validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    text = TextAreaField(label=('Основная часть поста'), validators=[InputRequired(), DataRequired(), Length(min=10, max=5000)])
    author = StringField(label=('Автор поста'), validators=[InputRequired(), DataRequired(), Length(max=240)])
    file = FileField(label=('Любой файл приложенный к посту'), validators=[])
    date = StringField(label=('Дата создания поста'))
    submit = SubmitField(label=('Подтвердить изменения'))


class SelectNewsForm(FlaskForm):
    post = SelectMultipleField(label=('ID'), validators=[Length(max=120000)])
    submit = SubmitField(label=('Выбрать пост'))


class ChangeNewsForm(FlaskForm):
    category = SelectMultipleField(label=('Изменить категорию'), validators=[])
    submit = SubmitField(label=('Подтвердить изменения'))




