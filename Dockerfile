FROM python:3.9.2-buster

ARG USERNAME=myuser

RUN useradd -m $USERNAME
WORKDIR /home/$USERNAME
USER root
ADD ./requirements.txt ./
ADD ./test_jwt.db ./
ADD ./main.py ./
RUN chown -R $USERNAME /home/myuser
USER myuser
ENV PATH $PATH:/home/${USERNAME}/.local/bin
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]