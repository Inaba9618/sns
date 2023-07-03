from flask import Flask, render_template
from flask import app

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)