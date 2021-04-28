from datetime import date, datetime

from cryptobot import db

from .enums import PositionType
from .telegram import send_message


class Position(db.Model):
    time = db.Column(db.DateTime, primary_key=True)
    symbol = db.Column(db.String(25), primary_key=True)
    position = db.Column(
        db.Enum("none", "long", "short", name="PositionType"), default="none"
    )

    def __repr__(self):
        return f"<Position (time: {self.time} symbol: {self.symbol} position: {self.position}>"


class EquityRecord(db.Model):
    time = db.Column(db.DateTime, primary_key=True)
    equity = db.Column(db.Float)
    assets = db.Column(db.String(250))

    def __repr__(self):
        return f"<Equity (time: {self.time} equity: {self.equity}>"


def get_position(dt, symbol):
    pos = Position.query.get((dt, symbol))

    if pos is not None:
        return pos
    else:
        return Position(time=dt, symbol=symbol, position=PositionType.NONE.value)


def get_current_equity():
    return EquityRecord.query.order_by(EquityRecord.time.desc()).first()


def get_equity_history():
    return EquityRecord.query.all()


def get_equity_history_within_time(frm, to):
    if frm is not None:
        return EquityRecord.query.filter(EquityRecord.time >= frm).filter(
            EquityRecord.time <= to
        )

    return EquityRecord.query.filter(EquityRecord.time <= to)


def add_position(dt, symbol, position):
    try:
        pos = Position.query.get((dt, symbol))
        if pos is not None:
            db.session.delete(pos)
        db.session.add(Position(time=dt, symbol=symbol, position=position.value))
        db.session.commit()

    except Exception as e:
        send_message(e)


def add_equity_record(dt, equity, assets):
    try:
        eq_rec = EquityRecord.query.get(dt)
        if eq_rec is not None:
            db.session.delete(eq_rec)
        db.session.add(EquityRecord(time=dt, equity=equity, assets=assets))
        db.session.commit()

    except Exception as e:
        send_message(e)
