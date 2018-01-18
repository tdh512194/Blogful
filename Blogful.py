import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

class Entry(db.Model):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(1024))
    content = Column(Text)
    datetime = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, title, content):
        self.title = title
        self.content = content


def seed(entry):
    """create and add blog post into db"""
    #entry = Entry(title, content)
    db.session.add(entry)
    db.session.commit()

@app.route('/')
def home():
    db.create_all()
    create()
    entry_id = [1, 2] #TODO: define with pagination
    entries = []
    for id in entry_id:
        entries.append(Entry.query.get(id));

    print type(entries)
    print entries
    return render_template('index.html', entries=entries)
    #return 'OK'

def create():
    content = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"""

    e1 = Entry('First post', content)
    e2 = Entry('Second post', content)
    e3 = Entry('Third post', content)
    e4 = Entry('Fourth one', content)


    seed(e1);
    seed(e2);
    seed(e3);
    seed(e4);


    return 'Created contents'



if __name__ == '__main__':
    app.run(debug=True)
