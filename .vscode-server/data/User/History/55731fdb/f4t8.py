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
        if len(field.data) < 4:
            raise ValidationError('パスワードは4文字以上で！')


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
    email = StringField('メールアドレス', validators=[DataRequired(), Email('メールアドレスでお願いマッスル')])
    comment = TextAreaField('一言コメント')
    picture_path = FileField('画像ファイルアップロード')
    submit = SubmitField('更新')


    