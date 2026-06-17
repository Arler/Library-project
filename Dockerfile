FROM python:3.13-slim
WORKDIR /libraryApp
COPY ./library .
COPY ./requirements.txt /libraryApp/
RUN pip install -r requirements.txt
CMD ["sh", "-c", "python manage.py makemigrations accounts && \
    python manage.py migrate accounts && \
    python manage.py migrate &&\
    python manage.py runserver 0.0.0.0:8000"]
EXPOSE 8000