from flask import Flask
from settings import APP_SETTINGS
app = Flask(__name__)
app.config.from_object(APP_SETTINGS)

print(APP_SETTINGS)


@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run()