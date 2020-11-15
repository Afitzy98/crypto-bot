from datetime import datetime
from cryptobot import db
from .enums import Position
from .telegram import send_message


class HourlyPosition(db.Model):
    time = db.Column(db.DateTime, primary_key=True)
    symbol = db.Column(db.String(10), primary_key=True)
    position = db.Column(
        db.Enum("none", "long", "short", name="Position"), default="none"
    )

    def __repr__(self):
        return f"<Position (time: {self.time} symbol: {self.symbol} position: {self.position}>"


def get_position(dt, symbol):
    pos = HourlyPosition.query.get((dt, symbol))

    if pos is not None:
        return pos
    else:
        return HourlyPosition(time=dt.now, symbol=symbol, position=Position.NONE.value)


def add_position(dt, symbol, position):
    try:
        db.session.add(HourlyPosition(time=dt, symbol=symbol, position=position.value))
        db.session.commit()

    except Exception as e:
        send_message(e)