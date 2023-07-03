from flask import Flask, render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300),nullable=False)
    created_at = db.Column(db.DateTime,nullable=False,default = datetime.now(pytz.timezone('Asia/Tokyo')))

@app.route('/')
def index():
    if request.method == "GET":
        posts =Post.query.all()
        return render_template('index.html' ,posts=posts)

@app.route('/create' ,methods = ["GET","POST"])
def create():
    if request.method == "POST":
        title = request.form.get('title')
        body = request.form.get('body')
        post=Post(title=title,body=body)
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html')

@app.route('/edit/<int:id>',methods = ["GET","POST"])
def edit(id):
    post = Post.query.get(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.body = request.form['body']
        db.session.commit()

        return redirect('/')
    else:
        return render_template("/edit.html",post=post)

@app.route('/delete/<int:id>',methods = ["GET"])
def delete():
    post = Post.query.get(id)

    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()

        return render_template("/")

    else:
        return render_template("/")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)