# encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort, jsonify
import config
from extdb import db
from models import *
import pymysql
from sqlalchemy import or_, desc
import time
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
pymysql.install_as_MySQLdb()


@app.route('/')
def hello_world():
    return 'Hello World!'

# 注册
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        account = request.form.get('account')
        telephone = request.form.get('telephone')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        intro = request.form.get('intro')

        # 默认头像
        head_img_url = 'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1540902584502&di=44019bc649a2cc6a8b1dca9ba57c4015&imgtype=0&src=http%3A%2F%2Fimg.zcool.cn%2Fcommunity%2F01460b57e4a6fa0000012e7ed75e83.png'

        if password != password2:
            return u"两次密码输入不一致"

        if account == None or account == '':
            return u"请输入手机号码"
        if password == None or password == '':
            return u"请输入密码"

        user = User.query.filter(User.account == telephone,
                                 User.password == password,
                                 User.telephone == telephone,
                                 User.email == email,
                                 User.username == username,
                                 User.head_img_url == head_img_url).first()

        if user:
            return u"该用户已存在"
        else:
            user = User(account=account,
                        password=password,
                        telephone=username,
                        email=email,
                        username=username,
                        intro=intro, )

            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))


# 登录
@app.route('/login/', methods=['GET', 'POST'])
def login():
    print(app.config)
    return '这里是登录页面'

# 注销
@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

# 通讯录
@app.route('/contacts/')
@login_required
def contacts():
    pass

# 朋友圈
@app.route('/friend_circle/', methods=['GET', 'POST'])
@login_required
def friend_circle():
    pass

# 查找
@app.route('/search/', methods=['GET', 'POST'])
def search():
    pass

# 用户信息
@app.route('/user_info/<user_id>')
@login_required
def user_info(user_id):
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
