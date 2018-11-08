# encoding: utf-8

from extdb import db
from datetime import datetime


# 用户
class User(db.Model):
    __tablename__ = 'user'  # 表名，不指定的话默认为小写处理后的类名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # now()获取的是服务器第一次运行的时间
    # now就是每次创建一个模型的时候，都获取当前的时间
    create_time = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    account = db.Column(db.String(20), nullable=False) # 账号
    password = db.Column(db.String(20), nullable=False) # 密码
    telephone = db.Column(db.String(11), nullable=True) # 手机号码
    email = db.Column(db.String(50), nullable=True) # 邮箱
    username = db.Column(db.String(20), nullable=True) # 用户名
    intro = db.Column(db.Text, nullable=True) # 简介
    head_img_url = db.Column(db.String(255), nullable=True) # 头像链接
    sex = db.Column(db.Integer) # 性别
    net_status = db.Column(db.Integer,default=0) # 网络状态

# 好友请求
class Friend_Request(db.Model):
    __tablename__ = 'friend_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 发送者
    target_id = db.Column(db.Integer, nullable=False)  # 发送对象

    state = db.Column(db.Integer, default=0)  # 状态 0：等待通过 1：通过请求 2：被拒绝 3：已失效
    sender = db.relationship('User', backref=db.backref('friend_requests'))  # 反向关联

# 好友绑定
class Friend_Bind(db.Model):
    __tablename__ = 'friend_bind'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    # 两个用户的id
    uid = db.Column(db.Integer, nullable=False)
    fid = db.Column(db.Integer, nullable=False)

# 朋友圈
class Friend_Circle(db.Model):
    __tablename__ = 'friend_circle'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 发布者
    user = db.relationship('User', backref=db.backref('friend_circles'))

    text = db.Column(db.Text)
    address = db.Column(db.String(200))
    weather = db.Column(db.String(20))

# 文件
class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)

    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 上传者
    uploader = db.relationship('User', backref=db.backref('files'))

    source_id = db.Column(db.Integer)  # 对应表id
    source_type = db.Column(db.Integer)  # 对应枚举类型


# 点赞
class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    friend_circle_id = db.Column(db.Integer,db.ForeignKey('friend_circle.id'))
    friend_circle = db.relationship('Friend_Circle',backref=db.backref('likes'))

    user_id = db.Column(db.Integer,nullable=False)

# 评论
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    friend_circle_id = db.Column(db.Integer,db.ForeignKey('friend_circle.id'))
    friend_circle = db.relationship('Friend_Circle',backref=db.backref('comments'))

    text = db.Column(db.Text,nullable=False)

    user_id = db.Column(db.Integer,nullable=False) # 发表评论者
    target_id = db.Column(db.Integer) # 对谁的评论，默认空