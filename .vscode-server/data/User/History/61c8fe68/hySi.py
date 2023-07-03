from flask import Flask

app = Flask(__name__)

# アプリケーションのルートやビュー関数などを定義する
@app.route('/')
def hello():  
    str ='hello'
    return str

if __name__ == '__main__':
    app.run(host='3.25.165.193', port=8080)
    