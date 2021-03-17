FROM python:3.9.2-buster

RUN useradd myuser 
USER myuser
WORKDIR /home/myuser

ADD ./requirements.txt ./
ADD ./test_jwt.db ./
ADD ./main.py ./
RUN pip3 install --user -r requirements.txt


ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
