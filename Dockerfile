# Use the Pyhton buster image
FROM 001712226679.dkr.ecr.eu-west-1.amazonaws.com/python3.8-buster:latest

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
ADD . /app

ARG APP_SECRET_KEY
ARG APP_SETTINGS
ARG BINANCE_API_KEY
ARG BINANCE_SECRET_KEY
ARG TG_BOT_TOKEN
ARG TG_USER_ID
ARG WEBHOOK_URL
ARG DB_URI

# Install the dependencies
RUN pip install -r requirements.txt

RUN pip install gunicorn

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]