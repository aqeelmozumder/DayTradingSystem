FROM python:latest

ADD Client.py /client/
ADD 1UserWorkload.txt /client/
ADD 10UserWorkload.txt /client/
ADD config.py /client
ADD host.cert /client/
ADD host.key /client/

CMD [ "python3", "./client/Client.py" ]