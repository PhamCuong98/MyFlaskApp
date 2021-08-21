from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(150))

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password

class data_articles(db.Model):
    __tablename__ = 'data_articles'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    daytime = db.Column(db.String(200))
    title = db.Column(db.Text())
    body = db.Column(db.Text())

    def __init__(self, username, daytime, title, body):
        self.username = username
        self.daytime = daytime
        self.title = title
        self.body = body