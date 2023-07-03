from flask import Flask

app = Flask(__name__)

# アプリケーションのルートやビュー関数などを定義する
@app.route('/')
def hello():  
    print('hello')

if __name__ == '__main__':
    app.run()