from Model import *
from flask import render_template, request, redirect, url_for

USER_ID = 0

def validate(username):
    global USER_ID
    user = User.query.get(USER_ID)
    if username == user.user_name:
        return True
    return False

@app.route('/')
def initialize():
    db.create_all()
    return redirect('/home')

@app.route('/home')
def home():
    entry_id = [1, 2] #TODO: define with pagination
    entries = []
    for id in entry_id:
        entries.append(Entry.query.get(id));
    return render_template('index.html',entries=entries)

@app.route('/login', methods=['GET','POST'])
def login():
    """Input > Querry > Login and Redirect to home/Re render with validation msg"""
    global USER_ID
    message = ''  # validation
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(user_name=username, password=md5(password.encode()).hexdigest()).first()
        if user:
            login_user(user=user)
        else:
            message = 'wrong username or password'
    if current_user.is_authenticated:
        USER_ID = user.id
        return redirect('/home')
    return render_template('login.html', message=message)

@app.route('/register',methods=['POST'])
def register():
    """Input > Add to DB > Redirect to login"""
    username = request.form['username']
    password = request.form['password']
    db.session.add(User(username,password))
    db.session.commit()
    return redirect('/login')

@app.route('/account')
def account():
    pass

@app.route('/<username>/write')
@login_required
def write(username):
    """render the blog writting page"""
    if validate(username):
        return render_template('write.html')
    return 'WRITE Not Allowed'

@app.route('/<username>/written')
@login_required
def written(username):
    """post the created entry to db > redirect to the created entry"""
    global USER_ID
    if validate(username):
        title = request.form['title']
        content = request.form['content']
        entry = Entry(title, content, owner_id=USER_ID)
        db.session.add(entry)
        db.session.commit()
        link = url_for('post',id=entry.id) #because redirect doesnt handle <var> syntax in url
        return redirect(link)

@app.route('/post/<id>')
def post(id):
    blogpost = Entry.query.get(id)
    return render_template('blogpost.html', title = blogpost.title, content = blogpost.content)

# def seed(entry):
#     """create and add blog post into db"""
#     #entry = Entry(title, content)
#     db.session.add(entry)
#     db.session.commit()

# @app.route('/')
# def home():
#     db.create_all()
#     create()
#     entry_id = [1, 2] #TODO: define with pagination
#     entries = []
#     for id in entry_id:
#         entries.append(Entry.query.get(id));
#
#     print type(entries)
#     print entries
#     return render_template('index.html', entries=entries)

# @app.route('/home')
# def homepage():
#     return render_template('index.html')
#

#

#
# @app.route('/written',methods=['POST'])
# def written():
#     """submit the written content to db and redirect to the post"""
#     title = request.form['title']
#     content = request.form['content']
#     entry = Entry(title,content)
#     db.session.add(entry)
#     db.session.commit()
#     link = url_for('post',id=entry.id) #because redirect doesnt handle <var> syntax in url
#     return redirect(link)
#
#
# def create():
#     content = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"""
#     e1 = Entry('First post', content)
#     e2 = Entry('Second post', content)
#     e3 = Entry('Third post', content)
#     e4 = Entry('Fourth one', content)
#
#     seed(e1);
#     seed(e2);
#     seed(e3);
#     seed(e4);
#     return 'Created contents'



if __name__ == '__main__':
    app.run(debug=True)
