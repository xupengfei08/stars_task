import os

from apscheduler.executors.pool import ThreadPoolExecutor


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2010415108'

    # 管理员邮箱
    STARS_TASK_ADMIN = 'xupengfei08@163.com'

    PER_PAGE_10 = 10
    PER_PAGE_5 = 5
    PER_PAGE_20 = 20

    # 邮箱配置
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    # 发送验证的邮箱信息
    MAIL_USERNAME = '13770270322@163.com'
    MAIL_PASSWORD = 'xpf157177xpf'
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    # 发件人
    STARS_TASK_MAIL_SENDER = 'STARS-TASK<13770270322@163.com>'
    # 邮件主题前缀
    STARS_TASK_MAIL_SUBJECT_PREFIX = '[STARS-TASK]'

    # CSRF:跨站请求伪造，关闭 CSRF 校验
    WTF_CSRF_ENABLED = False

    SCHEDULER_EXECUTORS = {
        'default': ThreadPoolExecutor(20)
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    # 开启定时任务API
    SCHEDULER_API_ENABLED = True


# 开发环境的配置
class DevelopmentConfig(Config):
    MONGODB_SETTINGS = {
        'db': 'stars_task',
        'host': '127.0.0.1',
        'port': 27017,
        'username': 'root',
        'password': '123456'
    }


# 生产环境的配置
class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'db': 'stars_task',
        'host': 'mongo',
        'port': 27017,
        'username': 'root',
        'password': '123456'
    }


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
