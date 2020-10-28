from signal import signal, SIGINT
from sys import exit
from twisted.internet import reactor

from cryptobot import app
from cryptobot.binance import socket_manager

def kill_websocket(signal_received, frame):
  print('SIGINT or CTRL-C detected. Exiting gracefully')
  if app.config.get("DEVELOPMENT") == False:
    socket_manager.close()
    reactor.stop()
  exit(0)

if __name__ == '__main__':
    signal(SIGINT, kill_websocket)
    app.run(threaded=True, port=3000)
    