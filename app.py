# encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import config
from extdb import db
from models import *
import pymysql
from sqlalchemy import or_, desc
import time
from decorators import login_required
import os
import hashlib
from flask_socketio import SocketIO, send, emit, join_room, leave_room, disconnect

app = Flask(__name__)
app.config.from_object(config)
pymysql.install_as_MySQLdb()
db.init_app(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')


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
            return u'两次密码输入不一致'

        if account == None or account == '':
            return u'请输入手机号码'
        if password == None or password == '':
            return u'请输入密码'

        user = User.query.filter(User.account == telephone,
                                 User.password == password,
                                 User.telephone == telephone,
                                 User.email == email,
                                 User.username == username,
                                 User.head_img_url == head_img_url).first()

        if user:
            return u'该用户已存在'
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
    if request.method == 'GET':
        return render_template('login.html')
    else:
        account = request.form.get('account')
        password = request.form.get('password')

        # print(request.args.get('account')) # 移动端请求方式

        user = User.query.filter(User.account == account,
                                 User.password == password).first()
        if user:
            if user.username == None or user.username == '':
                user.username = '用户%s' % (user.id)
                db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return u'账号或密码错误'


# 注销
@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


@app.context_processor
def my_context_processor():
    if 'iPhone' in request.headers.get('User-Agent'):
        request_device = 'phone'
    elif 'Android' in request.headers.get('User-Agent'):
        request_device = 'phone'

    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).one()
        if user:
            return {'login_required_user': user}
    return {}


# 查找
@app.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    keyword = request.form.get('search')
    like = '%%%s%%' % (keyword)
    id_like = int(keyword) if keyword != '' else 0
    users = User.query.filter(or_(User.username.like(like), User.id.like(id_like))).all()
    context = {
        'users': users
    }
    return render_template('search_users.html', **context)


# 用户信息
@app.route('/user_info/<user_id>/')
def user_info(user_id):
    user = User.query.filter(User.id == user_id).first()
    if user:
        my_user_id = session.get('user_id')
        canAdd = True
        if user.id == my_user_id:
            canAdd = False

        my_user_id = str(my_user_id)

        uid = min(user_id, my_user_id)
        fid = max(user_id, my_user_id)

        friend = Friend_Bind.query.filter(Friend_Bind.uid == uid,
                                          Friend_Bind.fid == fid).first()
        if friend:
            canAdd = False

        context = {
            'user_info': user,
            'canAdd': canAdd,
        }
        return render_template('user_info.html', **context)
    else:
        return u'没有该用户信息'


# 修改用户信息
@app.route('/edit_user_info/', methods=['GET', 'POST'])
@login_required
def edit_user_info():
    user_id = session.get('user_id')

    if request.method == 'GET':
        user = User.query.filter(User.id == user_id).first()
        context = {'user': user}
        return render_template('user_info_edit.html', **context)
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        intro = request.form.get('intro')
        head_img_url = None

        if len(request.files) != 0:
            file = request.files['img_file']
            res = upload_file('permanent', file, user_id)
            head_img_url = res['link']

        user = User.query.filter(User.id == user_id).first()
        user.username = username
        user.email = email
        user.telephone = telephone
        user.intro = intro
        user.head_img_url = head_img_url if head_img_url is not None else user.head_img_url

        db.session.commit()

        return u'用户信息修改成功'


# 发送好友请求
@app.route('/friend_request/', methods=['POST'])
@login_required
def friend_request():
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        user_id = session.get('user_id')

        if int(target_id) == int(user_id):
            return u'不能对自己发送好友请求'

        exist = Friend_Request.query.filter(Friend_Request.sender_id == user_id,
                                            Friend_Request.target_id == target_id).first()
        if exist:
            return u'不能重复发送请求'

        target = User.query.filter(User.id == target_id).first()
        if target:
            fr = Friend_Request(target_id=target.id)
            user = User.query.filter(User.id == user_id).first()
            fr.sender = user
            fr.sender_id = user.id
            fr.state = 0

            db.session.add(fr)
            db.session.commit()

            return u'申请添加好友成功'


# 好友请求列表
@app.route('/friend_request_list/')
@login_required
def friend_request_list():
    user_id = session.get('user_id')
    friendRs = Friend_Request.query.filter(Friend_Request.target_id == user_id,
                                           Friend_Request.state == 0).all()
    context = {
        'requests': friendRs
    }
    return render_template('friend_request_list.html', **context)


# 同意好友请求
@app.route('/agree_friend_request/<sender_id>')
@login_required
def agree_friend_request(sender_id):
    print(sender_id)
    user_id = str(session.get('user_id'))

    fr = Friend_Request.query.filter(Friend_Request.sender_id == sender_id,
                                     Friend_Request.target_id == user_id).first()
    if fr == None:
        return u'好友请求出现错误'

    fr.state = 1  # 设为通过状态

    # 让user1 < user2，方便处理
    uid = min(user_id, sender_id)
    fid = max(user_id, sender_id)

    exist = Friend_Bind.query.filter(Friend_Bind.uid == uid,
                                     Friend_Bind.fid == fid).first()
    if exist is not None:
        db.session.commit()
        return u'用户之间已经是好友，无法重复绑定'

    friend = Friend_Bind(uid=uid, fid=fid)
    db.session.add(friend)
    db.session.commit()

    return u'已同意该好友请求'


# 通讯录
@app.route('/address_list/')
@login_required
def address_list():
    user_id = session.get('user_id')
    binds = Friend_Bind.query.filter(or_(Friend_Bind.uid == user_id, Friend_Bind.fid == user_id)).all()

    friends = []
    for bind in binds:
        nid = None
        if bind.uid == user_id:
            nid = bind.fid
        else:
            nid = bind.uid
        friend = User.query.filter(User.id == nid).first()
        friends.append(friend)

    context = {'friends': friends}

    return render_template('address_list.html', **context)


# 朋友圈
@app.route('/friend_circle/', methods=['GET', 'POST'])
@login_required
def friend_circle():
    if request.method == 'GET':
        user_id = session.get('user_id')

        friends = Friend_Bind.query.filter(or_(Friend_Bind.uid == user_id,
                                               Friend_Bind.fid == user_id)).all()

        friend_id_list = []
        friend_id_list.append(user_id)

        for friend in friends:
            uid = friend.uid
            if uid == user_id:
                uid = friend.fid

            friend_id_list.append(uid)

        circles = Friend_Circle.query.filter(Friend_Circle.user_id.in_(friend_id_list)).order_by(
            desc(Friend_Circle.create_time)).limit(100).all()

        result = []
        for circle in circles:
            user = User.query.filter(User.id == circle.user_id).first()

            files = File.query.filter(File.uploader_id == user.id,
                                      File.source_id == circle.id).all()

            images = []
            for file in files:
                images.append(file.link)

            content = {
                'circle_id': circle.id,
                'username': user.username,
                'head_img_url': user.head_img_url,
                'text': circle.text,
                'user_id': user.id,
                'timestamp': time.mktime(circle.create_time.timetuple()),
                'images': images,
                'like_status': '点赞'
            }

            # 点赞列表
            likes = []
            for like in circle.likes:
                user = User.query.filter(User.id == like.user_id).first()
                dic = {
                    'user_id': user.id,
                    'username': user.username,
                    'head_img_url': user.head_img_url,
                }
                likes.append(dic)

                if like.user_id == user_id:
                    content['like_status'] = '已赞'

            if len(likes) != 0:
                content['likes'] = likes

            # 评论列表
            comments = []
            for comment in circle.comments:
                user = User.query.filter(User.id == comment.user_id).first()
                dic = {
                    'user_id': user.id,
                    'username': user.username,
                    'head_img_url': user.head_img_url,
                    'text': comment.text,
                }
                comments.append(dic)

            if len(comments) != 0:
                content['comments'] = comments

            result.append(content)
        context = {'result': result}
        return render_template('friend_circle.html', **context)
    else:
        return jsonify({'code': 1,
                        'result': 'null'})


# 编辑消息发布到朋友圈
@app.route('/friend_circle_release/', methods=['GET', 'POST'])
@login_required
def friend_circle_release():
    if request.method == 'GET':
        return render_template('friend_circle_release.html')
    else:
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()

        text = request.form.get('text')
        address = request.form.get('address')
        weather = request.form.get('weather')

        fc = Friend_Circle(user_id=user_id,
                           user=user,
                           text=text,
                           address=address,
                           weather=weather)
        db.session.add(fc)
        db.session.commit()

        for key in request.files:
            file = request.files[key]
            res = upload_file('permanent', file, user_id, fc.id, 0)

        return u'finish'


# 点赞
@app.route('/like/<friend_circle_id>/')
@login_required
def like(friend_circle_id):
    print(friend_circle_id)

    print(request.args)
    # return 'ok'
    my_user_id = session.get('user_id')

    fc = Friend_Circle.query.filter(Friend_Circle.id == friend_circle_id).first()
    if fc == None:
        return u'获取朋友圈索引id失败'

    exist = Like.query.filter(Like.user_id == my_user_id,
                              Like.friend_circle_id == friend_circle_id).first()
    if exist is not None:
        db.session.delete(exist)
        db.session.commit()
        return u'取消点赞成功'

    like = Like(friend_circle=fc,
                friend_circle_id=fc.id,
                user_id=my_user_id)

    db.session.add(like)
    db.session.commit()

    return u'点赞成功'


# 评论
@app.route('/comment/', methods=['GET', 'POST'])
@login_required
def comment():
    user_id = session.get('user_id')

    text = request.form.get('text')
    circle_id = request.form.get('circle_id')

    fc = Friend_Circle.query.filter(Friend_Circle.id == circle_id).first()

    comment = Comment(friend_circle_id=circle_id,
                      user_id=user_id,
                      friend_circle=fc,
                      text=text)
    db.session.add(comment)
    db.session.commit()

    return u'评论成功'


# 文件上传
@app.route('/upload_file/', methods=['POST'])
def upload():
    file = request.files['file']
    # res =


# 上传文件
# style: 路径，不同路径下的文件保存日期不同，如通讯时发送的文件只会短期保存，而朋友圈的文件除非用户删除否则不会被删除
# file: 要上传的文件
def upload_file(root, file, uploader_id=0, source_id=0, source_type=0):
    basePath = os.path.dirname(__file__)  # 当前文件所在路径
    # 保存文件时更名 md5(time + filename + ran(str)),保证不会重复，ran(str)还没做
    timestamp = int(time.time())
    joint = str(timestamp) + file.filename
    name = hashlib.md5(joint.encode('utf-8')).hexdigest()
    suffix = os.path.splitext(file.filename)[1]
    fullname = name + suffix

    filetype = suffix.strip('.')

    baseDir = os.path.dirname(__file__)
    fileDir = os.path.join(baseDir, 'files', root, filetype)
    if os.path.exists(fileDir) == False:
        os.mkdir(fileDir)  # 没有该类型文件的时候就创建一个

    path = os.path.join(fileDir, fullname)
    print(path)
    file.save(path)
    link = 'http://' + '127.0.0.1:5000' + '/download/' + root + '/' + filetype + '/' + fullname
    print(link)

    img = File(type=filetype,
               name=name,
               link=link, )

    if uploader_id != 0:
        uploader = User.query.filter(User.id == uploader_id).first()
        img.uploader_id = uploader_id
        img.uploader = uploader

    if source_id != 0:
        img.source_id = source_id

    if source_type != 0:
        img.source_type = source_type

    db.session.add(img)
    db.session.commit()

    return {'name': name,  # xxx
            'type': filetype,  # jpg
            'fullname': fullname,  # xxx.jpg
            'link': link}  # http://----/xxx.jpg


# 文件下载
# filetype: 文件类型,如txt、png、jpg
# filename: 文件名带后缀，如xxx.jpg
@app.route('/download/<root>/<filetype>/<fullname>', methods=['GET'])
def download(root, filetype, fullname):
    basePath = os.path.dirname(__file__)  # 当前文件所在路径
    path = os.path.join(basePath, 'files', root, filetype, fullname)
    if os.path.isfile(path):
        dir = str(root + '/' + filetype + '/' + fullname)
        return send_from_directory('files/', dir, as_attachment=True)  # as_attachment不加的话，会将内容直接显示在浏览器上
    return jsonify({'code': 1,
                    'result': u'下载文件失败'})


# 文件删除
@app.route('/delete_file/<root>/<filetype>/<fullname>', methods=['GET', 'POST'])
def delete_file(root, filetype, fullname):
    basePath = os.path.dirname(__file__)  # 当前文件所在路径
    path = os.path.join(basePath, 'files', root, filetype, fullname)
    if os.path.isfile(path):
        os.remove(path)
        return jsonify({'code': 0,
                        'result': u'文件下载成功'})
    return jsonify({'code': 1,
                    'result': u'删除文件失败'})

# SocketIO
@app.route('/socket/')
@login_required
def socket():
    return 'empty'
    return render_template('socket.html')

# socketio.on('connect') 连接成功时回调
# socketio.on('message') 接收字符串数据
# socketio.on('json') 接收json数据
# socketio.on('my event') 自定义消息，可以是字符串，字节，整数或者JSON
@socketio.on('connect')
def handle_connect():
    print(u'有客户端连接上服务器')
    socketio.send('server:欢迎你连接socket服务器')
    # send('socektio.send')
    # send_message_func('字符串数据接收测试顺利')  # 发送字符串
    # send_json_func({'result': 'json数据接收测试顺利'})  # 发送json，记得json参数要为True

    # arr = [1, 2, 3, '自定义消息数据接收测试顺利']
    # emit_custom_func('custom', arr)  # 自定义消息，要用emit

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端断开连接.')

# 发送数据函数
def send_message_func(message):
    socketio.send(message)
    # socketio.send(message, callback=cbk)
    # 名称空间用于区分用户，用户可以在连接地址后增加特定的路径，以达到标记不同用户的目的
    # 这里name='chat'，那么用户需要连接了ip:port/chat/ 之后，才能接受到该消息
    # socketio.send(message,namespace='/chat')

def cbk(data):
    print('客户端收到消息后回调: ' + data)


def send_json_func(json):
    socketio.send(json, json=True)


def emit_custom_func(custom, obj):
    socketio.emit(custom, obj)

# 发消息 1对1
@app.route('/send_msg_single/<target_id>', methods=['GET', 'POST'])
@login_required
def send_msg_single(target_id):
    if request.method == 'GET':
        my_user_id = session.get('user_id')

        user = User.query.filter(User.id == my_user_id).first()

        target_id = int(target_id)
        target = User.query.filter(User.id == target_id).first()

        context = {
            'target': target,
            'user': user,
        }
        return render_template('chat.html', **context)
    else:
        pass

@socketio.on('send_msg_single')
def send_msg_sin(data):
    print(data)
    sender_id = data['sender_id']
    target_id = data['target_id']
    msg = data['text']

    socketio.emit(target_id, data)

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    socketio.run(app,host='0.0.0.0',port=5000)