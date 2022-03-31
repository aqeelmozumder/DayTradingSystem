FROM python:latest
# FROM mongo:latest


ADD db.py /server/

RUN pip3 install yahoo_fin
RUN pip3 install pymongo

RUN pip3 install numpy

EXPOSE 65432

ADD WebServer.py /server/
ADD config.py /server/
ADD commands.py /server/
ADD commandsHelpers.py /server/
ADD transactions.py /server/

CMD [ "python3", "./server/WebServer.py" ]