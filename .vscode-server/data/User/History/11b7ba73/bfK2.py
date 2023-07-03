from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)


@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)