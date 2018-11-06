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