import datetime
from flask import Flask
from flask.ext.login import UserMixin,LoginManager
from hashlib import md5
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate, MigrateCommand,Manager
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

app.secret_key='blogfulproject'


login_manager=LoginManager()
login_manager.init_app(app)


class User(UserMixin,db.Model):
    __tablename__='user'
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_name = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    written_entry = db.relationship('Entry', backref='user', lazy=True) #WRITE rlts

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.setPassword(password)

    def setPassword(self, password):
        self.password = md5(password.encode()).hexdigest()


class Entry(db.Model):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(1024))
    content = Column(Text)
    datetime = Column(DateTime, default=datetime.datetime.now())
    owner_id = Column(Integer,ForeignKey('user.id'), nullable=False) #WRITE rlts

    def __init__(self, title, content, owner_id):
        self.title = title
        self.content = content
        self.owner_id = owner_id

