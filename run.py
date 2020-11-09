from cryptobot import app
from cryptobot.scheduler import scheduler


if __name__ == "__main__":
    scheduler.start()
    app.run(threaded=True, port=3001)
