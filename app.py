# encoding: utf-8

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login')
def login():
    return '这里是登录页面'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
