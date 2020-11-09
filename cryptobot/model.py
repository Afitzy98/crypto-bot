from cryptobot import db

class HourlyPosition(db.Model):
    time = db.Column(db.DateTime, primary_key=True)
    symbol = db.Column(db.String(10), primary_key=True)
    position = db.Column(
        db.Enum("none", "long", "short", name="Position"), default="none"
    )

    def __repr__(self):
        return "<Position %r>" % self.time
