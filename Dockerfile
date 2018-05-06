FROM python:3.6.4

ENV PYTHONUNBUFFERED 1

RUN mkdir /web/
ADD requirements.txt /web/

WORKDIR web

RUN pip install -r requirements.txt
ADD . /web/

# CMD ["python", "server.py"]