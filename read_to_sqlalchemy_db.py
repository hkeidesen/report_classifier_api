import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()


class Classified_reports(db.Model):
    __tablename__ = 'classiefied_reports'
    id = db.Column(db.Integer, primary_key=True)
    name = 1


    