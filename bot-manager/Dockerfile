FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/bots

WORKDIR $APP_HOME

COPY . $APP_HOME

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Set the entrypoint to run Gunicorn with your application
# Adjust the module path `app:app` to match your actual module and app name.
CMD python start.py
