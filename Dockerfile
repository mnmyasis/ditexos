FROM python:3.8

WORKDIR /home/www/
COPY . .

RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/home/www/entrypoint.sh"]