from apscheduler.jobstores.mongodb import MongoDBJobStore
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_apscheduler import APScheduler
from pymongo import MongoClient

from config import config
from pytz import utc

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = MongoEngine()

login_manager = LoginManager()
# 设置安全等级，防止用户回话被篡改（None,'basic','strong'）
# 设置为strong则Flask-Login会记住客户端ip和浏览器的用户代理信息，如果发现异动就登出用户
login_manager.session_protection = 'strong'
# 设置登录页面的端点，
login_manager.login_view = 'auth.login'
# 设置快闪消息，使用@login_required装饰器的路由要用到
login_manager.login_message = '该操作需要先登录账号'
# 动态配置定时任务
scheduler = APScheduler()


def create_app(config_name):
    app = Flask(__name__)
    # 导致指定的配置对象
    app.config.from_object(config[config_name])

    # 初始化扩展
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    scheduler.scheduler.add_jobstore(_init_iob_stores(app))
    scheduler.scheduler.timezone = utc
    scheduler.start()

    # 注册main蓝图
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册auth蓝图
    from .auth import auth as auth_blueprint
    # 使用url_prefix注册后，蓝本中定义的所有路由都会加上指定前缀，/login --> /auth/login
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册core蓝图
    from .core import core as core_blueprint
    app.register_blueprint(core_blueprint, url_prefix='/core')

    return app


# 定时作业存储(job store)
def _init_iob_stores(app):
    client = MongoClient(
        app.config['MONGODB_SETTINGS']['host'],
        app.config['MONGODB_SETTINGS']['port']
    )
    # 认证
    client[app.config['MONGODB_SETTINGS']['db']].authenticate(
        app.config['MONGODB_SETTINGS']['username'],
        app.config['MONGODB_SETTINGS']['password']
    )
    return MongoDBJobStore(database=app.config['MONGODB_SETTINGS']['db'], collection='job', client=client)
