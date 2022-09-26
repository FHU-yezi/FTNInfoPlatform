FROM python:3.8.10-alpine

ENV TZ Asia/Shanghai

RUN apk add --update tzdata

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    -r requirements.txt \
    --no-cache-dir \
    --no-compile \
    --disable-pip-version-check \
    --quiet \
    -i https://mirrors.aliyun.com/pypi/simple

COPY . .

CMD ["python", "main.py"]