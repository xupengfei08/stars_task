# app.route()装饰器把修饰的视图函数注册为路由
import datetime
import requests
import re

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from app.core import core
from app.core.forms import TaskForm
from app import scheduler

from app.models import ExecuteRecord, Task


@core.route('/tasks')
@login_required
def tasks():
    """
    任务列表
    """
    page = request.args.get('page', 1, type=int)
    pagination = Task.objects.order_by("-create_time").paginate(
        page=page,
        per_page=current_app.config['PER_PAGE_10']
    )
    tasks = pagination.items
    for task in tasks:
        task.job = scheduler.get_job(str(task.id))
    return render_template('core/tasks.html', tasks=tasks, pagination=pagination)


@core.route('/task', methods=['GET', 'POST'])
@login_required
def add_task():
    """
    新增任务
    """
    form = TaskForm()
    if form.validate_on_submit():
        # 初始化任务信息
        task = Task(
            name=form.name.data,
            desc=form.desc.data,
            trigger=form.trigger.data,
            time=form.time.data,
            url=form.url.data,
            method=form.method.data,
            create_user=current_user._get_current_object()
        )
        # 保存任务信息
        task.save()
        flash("新增任务成功")
        return redirect(url_for('core.tasks'))
    return render_template('core/task.html', form=form, type='add')


@core.route('/task/<id>', methods=['GET', 'POST'])
@login_required
def update_task(id):
    """
    修改任务
    """
    # 验证任务是否存在
    task = Task.objects(id=id).first()
    if not task:
        flash('任务不存在')
    else:
        form = TaskForm(data=task._data)
        if form.validate_on_submit():
            kwargs = dict(form.data)
            kwargs.pop('submit')
            kwargs['update_user'] = current_user._get_current_object()
            kwargs['update_time'] = datetime.datetime.utcnow()
            # 更新任务信息
            task.update(**kwargs)
            # 更新job任务
            modify_job(task)
            flash('操作成功')
        else:
            return render_template('core/task.html', form=form, type='update')
    return redirect(url_for('core.tasks'))


def add_job(task):
    """
    新增任务
    """
    trigger = task.trigger
    # 验证任务类型
    if trigger == 'interval':
        scheduler.add_job(
            id=str(task.id),
            func=task_run,
            name=task.name,
            trigger=trigger,
            seconds=int(task.time),
            args=(task,),
            replace_existing=True)
    elif trigger == 'date':
        scheduler.add_job(
            id=str(task.id),
            func=task_run,
            name=task.name,
            trigger=trigger,
            next_run_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=int(task.time)),
            args=(task,),
            replace_existing=True)
    elif trigger == 'cron':
        scheduler.add_job(
            id=str(task.id),
            func=task_run,
            name=task.name,
            trigger=trigger,
            second=task.time,
            args=(task,),
            replace_existing=True)


def modify_job(task):
    """
    修改任务
    """
    trigger = task.trigger
    # 验证任务类型
    if trigger == 'interval':
        scheduler.modify_job(
            id=str(task.id),
            name=task.name,
            trigger=trigger,
            seconds=int(task.time),
            args=(task,))
    elif trigger == 'date':
        scheduler.modify_job(
            id=str(task.id),
            name=task.name,
            trigger=trigger,
            next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=int(task.time)),
            args=(task,))
    elif trigger == 'cron':
        scheduler.modify_job(
            id=str(task.id),
            name=task.name,
            trigger=trigger,
            second=task.time,
            args=(task,))


@core.route('/task/<status>/<id>', methods=['POST'])
@login_required
def change_task_status(status, id):
    """
    改变任务状态
    (('add', '启动'),
    ('pause', '暂停'),
    ('run', '运行'),
    ('stop', '停止'))
    """
    # 验证任务是否存在
    task = Task.objects(id=id).first()
    if not task:
        flash('任务不存在')
    else:
        # 验证状态
        if status not in ('add', 'pause', 'run', 'stop'):
            flash('无效任务状态[' + status + ']')
            return redirect(url_for('core.tasks'))
        if status == 'add':
            add_job(task)
        else:
            job = scheduler.get_job(id)
            if not job:
                flash('任务未启动')
                return status
            if status == 'run':
                scheduler.resume_job(id)
            elif status == 'pause':
                scheduler.pause_job(id)
            elif status == 'stop':
                scheduler.remove_job(id)
        flash('操作成功')
    return status


@core.route('/task/<task_id>/execute/records')
@login_required
def task_execute_records(task_id):
    """
    任务执行记录列表
    """
    # 验证任务是否存在
    task = Task.objects(id=task_id).first()
    if not task:
        flash('任务不存在')
        return redirect(url_for('core.task'))
    else:
        name = task.name
        page = request.args.get('page', 1, type=int)
        pagination = ExecuteRecord.objects(task=task).order_by("-execute_time").paginate(
            page=page,
            per_page=current_app.config['PER_PAGE_10']
        )
        records = pagination.items
        return render_template('core/records.html', records=records, task=task, pagination=pagination)


def task_run(task):
    method = task.method
    url = task.url
    record = ExecuteRecord(
        task=task,
        execute_time=datetime.datetime.utcnow(),
    )
    try:
        if method and url:
            response = ''
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url)
            record.status = response.status_code == 200
            record.result = re.sub(r'\t|\r|\n', '', response.text)[0:128]
    except:
        record.result = '任务执行异常'
    # 保存执行记录
    record.save()
