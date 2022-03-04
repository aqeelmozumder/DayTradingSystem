FROM python:latest

ADD Client.py /client/
ADD Commands.txt /client/
ADD config.py /client

RUN pip3 install pymongo

RUN pip3 install numpy

CMD [ "python3", "./client/Client.py" ]