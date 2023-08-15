FROM mcr.microsoft.com/playwright/python:v1.37.0-jammy

WORKDIR /app

COPY ["pwright.py", "requirements.txt", "./"]

RUN pip install -r requirements.txt

CMD ["python", "pwright.py"]