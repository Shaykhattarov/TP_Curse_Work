import hashlib
import uuid

from datetime import datetime as dt
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=True)
    surname = db.Column(db.String(300), nullable=True)
    email = db.Column(db.String(2025), nullable=True)
    password = db.Column(db.String, nullable=True)
    old = db.Column(db.Integer, nullable=True)
    work = db.Column(db.String(300))
    img = db.Column(db.String(2025))

    def __repr__(self):
        return f'<user {self.id}>'

    def get_id(self):
        return self.id

    @staticmethod
    def hash_password(password):
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    @staticmethod
    def check_password(hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


class News(db.Model, UserMixin):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255), nullable=True)
    intro = db.Column(db.String(300), nullable=True)
    text = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(300), nullable=True)
    img = db.Column(db.String(10000), nullable=True)
    file = db.Column(db.String(10000), nullable=True)
    date = db.Column(db.DateTime, default=dt.utcnow())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self):
        return f'<news {self.id}>'


class Category(db.Model, UserMixin):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(2050), nullable=False)

    def __repr__(self):
        return f'<category {self.id}>'


class UserAuthorizationLog(db.Model, UserMixin):
    __tablename__ = 'user_authorization_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.VARCHAR(2050), nullable=True)
    date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<UserRegistrationLog {self.id}>'


class NewsCreatingLog(db.Model, UserMixin):
    __tablename__ = 'news_creating_log'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    author_name = db.Column(db.String(2050), nullable=False)
    news_title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<NewsCreatingLog {self.id}>'


