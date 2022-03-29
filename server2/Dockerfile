FROM python:latest
# FROM mongo:latest


ADD db.py /server2/

RUN pip3 install pymongo
RUN pip3 install numpy

EXPOSE 65433

ADD WebServer.py /server2/
ADD config.py /server2/
ADD commands.py /server2/
ADD commandsHelpers.py /server2/
ADD transactions.py /server2/

CMD [ "python3", "./server2/WebServer.py" ]