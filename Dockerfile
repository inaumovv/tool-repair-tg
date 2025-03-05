FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/src/tool-repair-tg/src

RUN pip install --upgrade pip

WORKDIR /usr/src/tool-repair-tg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /usr/src/tool-repair-tg/
WORKDIR /usr/src/tool-repair-tg/src/

ENTRYPOINT ["/usr/src/tool-repair-tg/entrypoint.sh"]