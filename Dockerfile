FROM python:3.11

# RUN apt-get update \
# 	&& apt-get install -y --no-install-recommends \
# 		postgresql-client \
# 	&& rm -rf /var/lib/apt/lists/*
COPY . /app

WORKDIR /app
COPY requirements.txt ./app
RUN pip install -r requirements.txt



# COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]