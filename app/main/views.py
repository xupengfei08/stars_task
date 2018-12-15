from flask import render_template
from flask_login import login_required

from app.main import main
from app.models import User


@main.route('/')
@login_required
def index():
    """
    主页
    """
    return render_template('index.html')


@main.route('/user/<name>')
@login_required
def user(name):
    """
    用户个人信息
    """
    user = User.objects(name=name).first_or_404()
    return render_template('user_info.html', user=user)


@main.route('/users')
@login_required
def users():
    """
    用户管理
    """
    users = User.objects()
    return render_template('users.html', users=users)
