FROM python:3.9
# define the present working directory
WORKDIR /app
COPY . .

# run pip to install the dependencies of the flask app
RUN pip install -r requirements.txt
# define the command to start the container
CMD ["python","main.py"]