from flask import (
    Flask, render_template, request, redirect, url_for, flash, 
)
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
from flaskr.models import User, UserConnect,Message,Post,Reply
from flaskr.forms import (
    LoginForm, RegisterForm, SettingForm, UserSearchForm, ConnectForm,MessageForm,PostForm,ReplyForm
)
from flaskr.models import db



@app.route('/', methods=['GET'])
def home():
    connect_form = ConnectForm()
    post = Post.query.all()
    users = [post.user for post in post]
    for user in users:
        print(user.username)
    friends = requested_friends = None
    if current_user.is_authenticated:
        friends = User.select_friends()
        requested_friends = User.select_requested_friends()
    else:
        return redirect(url_for('login'))
    return render_template('home.html', 
    friends=friends, requested_friends=requested_friends, connect_form=connect_form,posts=post,user=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.select_by_email(email)
        if user and user.check_password(password):
            """ ユーザに対してログイン処理を施す """
            login_user(user)
            return redirect(url_for('home'))
        elif user:
            flash('パスワードが間違っています')
        else:
            flash('存在しないユーザです')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username, email, password)
        with db.session.begin_nested():
            db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """ 要はパスワードをアップグレードしたい """
    form = LoginForm(request.form)
    user = None
    if request.method == 'POST':
        email = form.email.data
        user = User.select_by_email(email)
        if form.password.data:
            with db.session.begin_nested():
                user.reset_password(form.password.data)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('forgot_password.html', form=form, user=user)
    return render_template('forgot_password.html', form=form, user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    form = SettingForm(request.form)
    user_id = current_user.get_id()
    if request.method == 'POST':
        user = User.select_by_id(user_id)
        with db.session.begin_nested():
            user.username = form.username.data
            user.email = form.email.data
            user.update_at = datetime.now()
            if form.comment.data:
                user.comment = form.comment.data
            # fileの中身を読込
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_images/' + file_name
                # picture_pathの箱にfileの中身を書き込む
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_images/' + file_name
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('setting.html', form=form)

@app.route('/user_search', methods=['GET', 'POST'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    users = None
    if request.method == 'GET':
        users = User.query.all()
    elif request.method == 'POST' and form.validate():
        users = User.select_by_username(form.username.data)
        if users:
            return render_template('user_search.html', form=form, connect_form=connect_form, users=users)
        flash('ユーザが存在しません')
    return render_template('user_search.html', form=form, connect_form=connect_form, users=users)


@app.route('/user_connect', methods=['POST'])
@login_required
def user_connect():
    form = ConnectForm(request.form)
    if form.connect_status.data == 'apply':
        from_user_id = current_user.get_id()
        to_user_id = form.to_user_id.data
        connect = UserConnect(from_user_id, to_user_id, status=1)
        with db.session.begin_nested():
            db.session.add(connect)
        db.session.commit()
    elif form.connect_status.data == 'approve':
        from_user_id = form.to_user_id.data
        to_user_id = current_user.get_id()
        connect = UserConnect.select_connect(from_user_id, to_user_id)
        with db.session.begin_nested():
            connect.status = 2
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete_connect', methods=['POST'])
@login_required
def delete_connect():
    id = request.form['id']
    connect = UserConnect.select_id(id, current_user.get_id())
    with db.session.begin_nested():
        db.session.delete(connect)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/message/<to_user_id>', methods=['GET', 'POST'])
@login_required
def message(to_user_id):  # Homeからurl_forで受け取る
    is_friend = UserConnect.is_friend(to_user_id)
    if not is_friend:
        # 友達じゃなったらホームに返す
        return redirect(url_for('home'))
    form = MessageForm()
    from_user_id = current_user.get_id()
    friend = User.select_by_id(to_user_id)
    messages = Message.select_messages(to_user_id)

    if request.method == 'POST':
        """ 投稿があればDBをアップグレードして更新 """
        message = request.form['message']
        new_message = Message(from_user_id, to_user_id, message)
        with db.session.begin_nested():
            db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('message', to_user_id=friend.id))
    return render_template('message.html', form=form, friend=friend, messages=messages)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        title = form.title.data
        print("title:", title) 
        detail = form.detail.data
        post = Post(user_id=user_id, title=title, detail=detail)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template('create_post.html', form=form)

@app.route('/post_detail/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    user = post.user
    print(post)
    print(user.username)
    form = ReplyForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        content = form.content.data
        reply = Reply(user_id=user_id, post_id=post_id, content=content)
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post_id))
    
    return render_template('post_detail.html', post=post, form=form,user=user)

@app.route('/delete_post/<int:post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    print(post_id)
    Reply.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)