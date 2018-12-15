import hashlib
from datetime import datetime

from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Permission:
    """
    权限常量类
    """
    # 喜欢某篇文章
    FAVOURITE = 1
    # 评论
    COMMENT = 2
    # 写博客
    WRITE = 4
    # 管理员
    ADMIN = 8


class User(UserMixin, db.Document):
    """
    用户信息Model
    """
    email = db.EmailField(unique=True, max_length=64)
    name = db.StringField(unique_with='email', max_length=64)
    password_hash = db.StringField(required=True)
    confirmed = db.BooleanField(default=False)
    create_time = db.DateTimeField(default=datetime.utcnow(), required=True)
    # 邮箱地址的md5值
    avatar_hash = db.StringField(max_length=64, required=True)
    meta = {'collection': 'user'}

    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password属性不可读')

    # 计算密码的散列值
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 核对密码，即比较输入密码的散列值和原密码的散列值
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成令牌字符串
    # 初次注册时发送用户信息确认邮件需要使用
    def generate_confirmation_token(self, expiration=3600):
        # 生成有过期时间的签名
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # 序列化
        return s.dumps({'confirm': str(self.id)}).decode('utf-8')

    # 校验令牌字符串
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 反序列化
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != str(self.id):
            return False
        current_user.update(confirmed=True)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': str(self.id)}).decode('utf-8')

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """
        生成用户头像地址
        :param size:图片大小
        :param default:指定图片生成器
        :param rating:图片级别
        :return:
        """
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def is_administrator(self):
        """
        是否是管理员
        :return:
        """
        return True

    def __str__(self):
        return "email:{} - name:{} - ct:{}".format(self.email, self.name, self.create_time)


class AnonymousUser(AnonymousUserMixin):
    """
    未登录的用户类
    """
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


# Flask-Login的回调函数，用来加载用户信息
@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.objects(id=user_id).first()
    except User.DoesNotExist:
        user = None
    return user


TASK_TYPES = (('date', '单次任务'),
            ('cron', '定时任务'),
            ('interval', '循环任务'))


METHODS = (('GET', 'GET'),
            ('POST', 'POST'))


TASK_STATUS = (('init', '初始化'),
            ('pause', '暂停'),
            ('run', '运行'),
            ('stop', '停止'))


class Task(db.Document):
    """
    任务信息Model
    """
    # 任务名称
    name = db.StringField(unique=True, max_length=64)
    # 任务简述
    desc = db.StringField(max_length=200)
    # 任务类型
    trigger = db.StringField(required=True, choices=TASK_TYPES)
    # 触发时间
    time = db.StringField(required=True)
    # http执行器相关
    # 执行器地址
    url = db.URLField(required=True)
    # 执行器方法
    method = db.StringField(required=True, choices=METHODS)
    # 修改时间
    update_time = db.DateTimeField(default=datetime.utcnow(), required=True)
    # 修改人
    update_user = db.ReferenceField(User)
    # 创建时间
    create_time = db.DateTimeField(default=datetime.utcnow(), required=True)
    # 创建人
    create_user = db.ReferenceField(User)


class ExecuteRecord(db.Document):
    """
    任务执行记录Model
    """
    # 执行任务ID
    task = db.ReferenceField(Task)
    # 执行时间
    execute_time = db.DateTimeField(default=datetime.utcnow(), required=True)
    # 执行状态
    status = db.BooleanField(required=True, default=False)
    # 执行结果
    result = db.StringField(required=True)
