FROM python:3.9-slim
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y tzdata --no-install-recommends \
 && apt-get install -y gcc g++ libxml2-dev libxslt-dev libz-dev
COPY requirements.txt /
RUN echo "**** install python packages ****" \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /requirements.txt /tmp/* /var/tmp/* /var/lib/apt/lists/*
COPY . /
VOLUME /config
ENTRYPOINT ["python3", "plex_meta_manager.py"]
