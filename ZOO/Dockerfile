FROM python:3.9-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install -r requirements.txt
#COPY entrypoint.sh entrypoint.sh
#RUN chmod +x entrypoint.sh
COPY . .
CMD ["gunicorn", "--bind", ":8000", "--workers", "4","--worker-class", "gevent", "--timeout", "300", "ZOO.wsgi:application"]
