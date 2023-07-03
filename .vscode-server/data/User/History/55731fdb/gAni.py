from wtforms.form import Form
from wtforms.fields import (
    IntegerField, StringField, TextAreaField, PasswordField,
    HiddenField, SubmitField, FileField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flaskr.views import User


class LoginForm(Form):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    conf_password = PasswordField('確認用パスワード', validators=[DataRequired(), EqualTo('password', message='元のパスワードと一致しません')])
    submit = SubmitField('ログイン')

    def validate_password(self, field):
        if len(field.data) < 1:
            raise ValidationError('パスワードは1文字以上で！')


class RegisterForm(Form):
    username = StringField('ユーザ名', validators=[DataRequired()])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    conf_password = PasswordField('確認用パスワード', validators=[DataRequired(), EqualTo('password', message='元のパスワードと一致しません')])
    submit = SubmitField('ユーザ登録')

    def validate_email(self, field):
        if User.select_by_email(field.data):
            raise ValidationError('すでに登録されているメールアドレスです')

class SettingForm(Form):
    username = StringField('ユーザ名', validators=[DataRequired()])
    email = StringField('メールアドレス', validators=[DataRequired(), Email('メールアドレス')])
    comment = TextAreaField('プロフィール概要')
    picture_path = FileField('画像ファイルアップロード')
    submit = SubmitField('更新')

class UserSearchForm(Form):
    username = StringField('ユーザ名', validators=[DataRequired()])
    submit = SubmitField('ユーザ検索')

class ConnectForm(Form):
    to_user_id = HiddenField()
    connect_status = HiddenField()
    submit = SubmitField()

class MessageForm(Form):
    to_user_id = HiddenField()
    message = TextAreaField('メッセージを入力', validators=[DataRequired()], default='')
    submit = SubmitField('送信する')

class PostForm(Form):
    title = StringField('投稿タイトル', validators=[DataRequired()])
    detail = TextAreaField('詳細', validators=[DataRequired()])
    submit = SubmitField('投稿する')

class ReplyForm(Form):
    content = TextAreaField('返信内容', validators=[DataRequired()])
    submit = SubmitField('返信する')