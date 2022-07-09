FROM python:3.8.13-slim-bullseye
WORKDIR /usr/src/app
COPY src/requirements.txt ./
RUN pip3 install -r requirements.txt
COPY src/main.py .
CMD ["python3", "-u", "main.py"]