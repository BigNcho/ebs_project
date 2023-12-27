
FROM python:3.10.9

COPY . /app

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt


CMD ["python", "./smi_trans.py"]
