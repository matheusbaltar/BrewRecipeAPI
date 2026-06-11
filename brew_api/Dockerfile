FROM python:3.12-slim

WORKDIR /app

COPY brew_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "brew_api/manage.py", "runserver", "0.0.0.0:8000"]