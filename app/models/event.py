from .. import db


class Event(db.Model):
    __tablename__ = 'Event'

    name = db.Column(db.String, primary_key=True)
    logs = db.relationship("Log", backref="event", order_by=db.asc("date_modified"))

    def __repr__(self):
        return str(self.name)
