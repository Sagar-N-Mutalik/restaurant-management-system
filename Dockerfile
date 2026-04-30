FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . /app/
EXPOSE 8000

RUN python manage.py collectstatic --noinput

# 1. ADD THIS: Make the script executable
RUN chmod +x entrypoint.sh

# 2. REPLACE THE OLD CMD: Tell Docker to run the script
CMD ["bash", "entrypoint.sh"]