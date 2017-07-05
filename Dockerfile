FROM ubuntu:16.04

ENV LANG C.UTF-8

RUN apt update
RUN apt install -y ffmpeg python3 python3-pip git sqlite3

RUN git clone https://github.com/hobozhang/pyusic.git
RUN pip3 install --upgrade pip
RUN pip3 install -r pyusic/requirements.txt

VOLUME ["/pyusic/app/static"]
RUN mkdir -p pyusic/app/static/tmp
RUN mkdir -p pyusic/db
RUN cd /pyusic && python3 db_create.py 
RUN cd /pyusic && python3 db_migrate.py

EXPOSE 5000
WORKDIR /pyusic
CMD python3 run_server.py
