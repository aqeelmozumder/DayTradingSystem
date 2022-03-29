FROM python:latest

ADD QuoteServer.py /quoteserver/
ADD config.py /quoteserver/

RUN pip3 install yahoo_fin
RUN pip3 install pymongo

RUN pip3 install numpy

EXPOSE 65438

CMD [ "python3", "./quoteserver/QuoteServer.py" ]