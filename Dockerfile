FROM python:3.10.8-slim

# copy files and install requirements
COPY . /app
WORKDIR /app

# install dependencies
RUN pip install -r requirements.txt

# startup command
CMD ["python", "./src/main.py"]