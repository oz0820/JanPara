FROM python:3.9.17-slim-bullseye

WORKDIR app/

RUN apt-get update && apt-get upgrade -y

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]
