FROM python:3.8
# define the present working directory

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# run pip to install the dependencies of the flask app
RUN pip install -r requirements.txt

# define the command to start the container
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app