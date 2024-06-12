FROM python:3.10.8-slim

# copy files and install requirements
COPY . /app
WORKDIR /app

# install dependencies
RUN pip install .

# startup command
CMD ["python", "./src/main.py"]
