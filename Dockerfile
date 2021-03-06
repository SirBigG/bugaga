FROM python:3.7.2-alpine3.9

ENV PYTHONUNBUFFERED 1

RUN apk update && apk add dcron curl wget rsync ca-certificates && rm -rf /var/cache/apk/*

RUN apk --no-cache add autoconf automake postgresql-dev gcc python3-dev musl-dev g++ \
                       libxml2-dev \
                       libxslt-dev \
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       build-base \
                       linux-headers \
                       pcre-dev \
                       git \
                       openblas-dev

# Install data science libs
RUN pip install --no-cache-dir numpy scikit-learn

RUN mkdir /web/
ADD requirements.txt /web/
RUN pip install --no-cache-dir -r /web/requirements.txt

WORKDIR web
ADD . /web/
