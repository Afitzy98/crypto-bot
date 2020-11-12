from flask import Flask, request

from cryptobot import create_app

app = create_app()

if __name__ == "__main__":
    app.app_context().push()
    app.run(threaded=True, use_reloader=False)
