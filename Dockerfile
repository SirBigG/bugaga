FROM python:3.6.4

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get --assume-yes install cron

ADD crontab /etc/cron.d/parser-cron

RUN chmod 0644 /etc/cron.d/parser-cron

# RUN touch /var/log/cron.log

RUN mkdir /web/
ADD requirements.txt /web/
RUN pip install -r /web/requirements.txt

WORKDIR web
ADD . /web/

# CMD ["python", "server.py"]
