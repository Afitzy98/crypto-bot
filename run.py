from cryptobot import app
from cryptobot.scheduler import start_scheduler

if __name__ == "__main__":
    app.run(threaded=True, port=3001)
    start_scheduler()
