from cryptobot import app


if __name__ == "__main__":
    app.run(threaded=True, port=3000, use_reloader=False)
