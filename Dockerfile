FROM python:3.10.9-bullseye as builder

WORKDIR /builder

RUN apt update && apt install -y git && \
    pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN python -m pip wheel --no-cache-dir --wheel-dir=./wheels -r requirements.txt


FROM python:3.10.9-bullseye 

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=builder /builder/wheels wheels

RUN apt update && apt install -y ffmpeg\
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache wheels/* && rm -rf wheels

COPY . /app/

CMD python -m vsbot
