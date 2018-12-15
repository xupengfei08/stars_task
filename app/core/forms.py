from flask_wtf import FlaskForm

from wtforms.fields import HiddenField, StringField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, URL

from app.models import TASK_TYPES, METHODS


class TaskForm(FlaskForm):
    """
    任务表单
    """
    id = HiddenField(
        '任务ID',
        validators=[
            Length(0, 64, message='任务ID长度不超过64个字符')
        ]
    )
    name = StringField(
        '任务名称',
        validators=[
            DataRequired(),
            Length(1, 10, message='任务名称长度不超过10个字符')
        ]
    )
    desc = TextAreaField(
        '任务简述',
        validators=[
            DataRequired(),
            Length(0, 1024, message='任务简述长度不超过1024个字符')
        ],
        render_kw={'rows': '5', 'placeholder': '对于任务进行简要描述'}
    )
    trigger = RadioField(
        '任务类型',
        choices=TASK_TYPES,
        validators=[
            DataRequired()
        ],
        default=TASK_TYPES[0][0]
    )
    time = StringField(
        '触发时间',
        validators=[
            DataRequired()
        ]
    )
    url = StringField(
        '触发地址',
        validators=[
            DataRequired(),
            URL(message='URL地址格式有误')
        ]
    )
    method = RadioField(
        '触发方法',
        choices=METHODS,
        validators=[
            DataRequired()
        ],
        default=METHODS[0][1]
    )
    submit = SubmitField("提交")

    # validate_字段名 的方法和常规的验证函数一起被调用
    # def validate_email(self, field):
    #     if User.objects(email=field.data).first():
    #         raise ValidationError('邮箱已被注册')
