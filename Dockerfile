FROM python:3.7

LABEL maintainer="xpf@facemeng.com.cn"

RUN mkdir -p /usr/local/src/stars_task

WORKDIR /usr/local/src/stars_task

COPY . ./

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python", "./manage.py", "runserver" ]