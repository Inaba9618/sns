""" DBのtable設計とCRUDメソッド群 """

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flaskr.views import app
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
import os
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import aliased

DB_URI = 'sqlite:///sns.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.urandom(24)

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    """ LoginManagerをDBに対して動作させるためのメソッド """
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    """ ログインセッションを管理するUserテーブル """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(db.Text)
    comment = db.Column(db.Text, default='')
    picture_path = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # login_managerで必要
    create_at = db.Column(db.DateTime, default=datetime.now)  # datetime.now()では変になる
    update_at = db.Column(db.DateTime, default=datetime.now)
    
    def __init__(self, username, email, password):
        """ ユーザ名、メール、パスワードが入力必須 """
        self.username = username
        self.email = email
        self.password = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """ パスワードをチェックしてTrue/Falseを返す """
        return check_password_hash(self.password, password)

    def reset_password(self, password):
        """ 再設定されたパスワードをDBにアップデート """
        self.password = generate_password_hash(password).decode('utf-8')

    @classmethod
    def select_by_id(cls, id):
        """ UserテーブルからidでSELECTされたインスタンスを返す """
        return cls.query.get(id)

    @classmethod
    def select_by_email(cls, email):
        """ UserテーブルからemailでSELECTされたインスタンスを返す """
        return cls.query.filter_by(email=email).first()


    @classmethod
    def select_by_username(cls, username):
        return cls.query.filter(
            cls.username.like(f'%{username}%'),  # 両方向部分一致検索
            cls.id != int(current_user.get_id()),
        ).all()
    @classmethod
    def select_friends(cls):
        """ UserConnectを紐づけて、current_userとstatus==2のUserインスタンスを返す """
        return cls.query.join(
            UserConnect,
            or_(
                and_(
                    UserConnect.from_user_id == current_user.get_id(),
                    UserConnect.to_user_id == cls.id,  # 返す予定のユーザid
                    UserConnect.status == 2,
                ),
                and_(
                    UserConnect.from_user_id == cls.id,
                    UserConnect.to_user_id == current_user.get_id(),  # 返す予定のユーザid
                    UserConnect.status == 2,
                ),
            ),
        ).all()

    @classmethod
    def select_requested_friends(cls):
        """ UserConnectを紐づけて、current_userをtoとしてstatus==1のUserインスタンスを返す """
        return cls.query.join(
            UserConnect,
            and_(
                UserConnect.from_user_id == cls.id,
                UserConnect.to_user_id == current_user.get_id(),
                UserConnect.status == 1,
            ),
        ).all()


class UserConnect(db.Model):
    """ Userの友達状態を記録するテーブル """
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # user.idを外部キーとする
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # user.idを外部キーとする
    status = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.now)  # datetime.now()では変になる
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, from_user_id, to_user_id, status=0):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.status = status

    @classmethod
    def select_connect(cls, from_user_id, to_user_id):
        """ fromとtoを指定してSELECTされた友達関係を返す """
        return cls.query.filter_by(
            from_user_id = from_user_id,
            to_user_id = to_user_id
            ).first()

    @classmethod
    def select_id(cls, id1, id2):
        """ 1対の友達関係をSELECTして友達関係を返す """
        return cls.query.filter(
            or_(
                and_(
                    UserConnect.from_user_id == id1,  # Class.が必要
                    UserConnect.to_user_id == id2,  # filter_byと違って== になる
                ),
                and_(
                    UserConnect.from_user_id == id2,
                    UserConnect.to_user_id == id1,
                ),
            ),
        ).first()
    
    @classmethod
    def select_by_username(cls, username):
        """ UserConnectと外部結合させた上で、UserテーブルからusernameでSELECTされたインスタンスを返す """
        user_connect1 = aliased(UserConnect)  # UserConnectと紐づけられたクエリ
        user_connect2 = aliased(UserConnect)
        return cls.query.filter(
            cls.username.like(f'%{username}%'),  # 両方向部分一致検索
            cls.id != int(current_user.get_id()),
        ).outerjoin(  # UserConnectと外部結合
            user_connect1,
            and_(  # fromが自分
                user_connect1.from_user_id == current_user.get_id(),
                user_connect1.to_user_id == cls.id,
            )
        ).outerjoin(
            user_connect2,
            and_(  # fromが相手
                user_connect2.from_user_id == cls.id,
                user_connect2.to_user_id == current_user.get_id(),
            )
        ).with_entities(
            cls.id, cls.username, cls.picture_path, cls.comment,
            user_connect1.status.label('joined_status_from_currentuser'),
            user_connect2.status.label('joined_status_from_user'),
        ).all()


    @classmethod
    def select_by_username(cls, username):
        """ UserConnectと外部結合させた上で、UserテーブルからusernameでSELECTされたインスタンスを返す """
        user_connect1 = aliased(UserConnect)  # UserConnectと紐づけられたクエリ
        user_connect2 = aliased(UserConnect)
        return cls.query.filter(
            cls.username.like(f'%{username}%'),  # 両方向部分一致検索
            cls.id != int(current_user.get_id()),
        ).outerjoin(  # UserConnectと外部結合
            user_connect1,
            and_(  # fromが自分
                user_connect1.from_user_id == current_user.get_id(),
                user_connect1.to_user_id == cls.id,
            )
        ).outerjoin(
            user_connect2,
            and_(  # fromが相手
                user_connect2.from_user_id == cls.id,
                user_connect2.to_user_id == current_user.get_id(),
            )
        ).with_entities(
            cls.id, cls.username, cls.picture_path, cls.comment,
            user_connect1.status.label('joined_status_from_currentuser'),
            user_connect2.status.label('joined_status_from_user'),
        ).all()
    
    @classmethod
    def is_friend(cls, to_user_id):
            result = cls.query.filter(
                or_(
                    and_(
                        UserConnect.from_user_id == current_user.get_id(),
                        UserConnect.to_user_id == to_user_id,
                        UserConnect.status == 2,
                    ),
                    and_(
                        UserConnect.from_user_id == to_user_id,
                        UserConnect.to_user_id == current_user.get_id(),
                        UserConnect.status == 2,
                    ),
                ),
            ).first()
            if result:
                return True
            else:
                return False




class Message(db.Model):
    """ メッセージを記録するテーブル """
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, from_user_id, to_user_id, message):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message = message

    @classmethod
    def select_messages(cls, friend_id):
        return cls.query.filter(
            or_(
                and_(
                    Message.from_user_id == current_user.get_id(),
                    Message.to_user_id == friend_id,
                ),
                and_(
                    Message.from_user_id == friend_id,
                    Message.to_user_id == current_user.get_id(),
                ),
            ),
        ).all()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime, nullable=False,default=datetime.now)
    replies = db.relationship('Reply', backref='post', lazy=True)
    user = db.relationship('User', backref='post')


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    reply_date = db.Column(db.DateTime, nullable=False, default=datetime.now)