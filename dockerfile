FROM python:3.12.5-slim-bookworm
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY main.py .
CMD ["python3", "-u", "main.py"]
