import signal

from cryptobot import app
from cryptobot.scheduler import start_scheduler, shutdown_scheduler

if __name__ == "__main__":
    app.run(threaded=True, port=3001)
    start_scheduler()
    signal.signal(signal.SIGTERM, lambda signum, frame: shutdown_scheduler())
