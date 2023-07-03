from wtforms.form import Form
from wtforms.fields import IntegerField, StringField, SubmitField


class LikeAnimeForm(Form):
    name = StringField('名前：')
    like_anime = StringField('好きなアニメは：')
    rate = IntegerField('点数をつけるなら：')

