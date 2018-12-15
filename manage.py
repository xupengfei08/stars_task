# 启动程序
import os

from flask_script import Manager, Shell, Server
from app import create_app, db
from app.models import User, Permission

# 创建app
app = create_app(os.getenv('FLASK_ENV') or 'default')
manager = Manager(app)


# 程序、数据库实例、数据模型，这些对象可直接导入shell
def shell_context():
    return dict(app=app, db=db, User=User, Permission=Permission)


# 集成自定义shell命令
# python manage.py {shell, db, test, runserver}
manager.add_command('shell', Shell(make_context=shell_context))


# 命令管理的实例化
# python manage.py runserver
manager.add_command('runserver', Server(
    # use_debugger=True,
    # use_reloader=True,
    host='0.0.0.0',
    port=5000)
)

if __name__ == "__main__":
    manager.run(default_command='runserver')
