
FROM python:3.10.9

COPY . /app

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt


# Dockerfile


# Install Java
RUN apt-get update && \
    apt-get install -y default-jre

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/default-java



CMD ["python", "./nongdam.py"]
