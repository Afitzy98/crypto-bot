# Use the Pyhton buster image
FROM 001712226679.dkr.ecr.eu-west-1.amazonaws.com/python3.8-buster:latest

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
ADD . /app

ENV APP_SECRET_KEY=908110db-d9a6-4c72-a19d-7e65f653b598
ENV APP_SETTINGS=config.DevelopmentConfig
ENV BINANCE_API_KEY=YaAsOjDn4kTaQ82Ah4L3dfvwOOXdPq765C2z54ILBEsYnIvTzaM56LPjRpShR2OD
ENV BINANCE_SECRET_KEY=T3smzLvS5GkZobcCLufTLlXnfKiBsasz2LaRUIG5aOGV2xw8BjWwMj9wEQLhCCVA
ENV TG_BOT_TOKEN=1293170257:AAHZrOdSu1FSgptOgYepf5BoYqaYXVGGmng
ENV TG_USER_ID=1116362707
ENV WEBHOOK_URL=https://dev.cryptotradebot.tech/
ENV DB_PASSWORD=Fitzy2020

# Install the dependencies
RUN pip install -r requirements.txt

RUN pip install gunicorn

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app", "--preload"]