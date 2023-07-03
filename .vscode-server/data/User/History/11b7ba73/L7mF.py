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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)