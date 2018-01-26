from math import ceil
from Model import *
from flask import render_template, request, redirect, url_for
from flask.ext.login import login_user,current_user,logout_user,login_required


#if current_user is None:
USER_ID = 0  # current user_id, is set to 0 when log out
post_per_page = 4
current_page = 1


def validate(username):
    global USER_ID
    print USER_ID
    user = User.query.get(USER_ID)
    print user
    if username == user.user_name:
        return True
    return False

def own(entry_id):
    global USER_ID
    entry = Entry.query.get(entry_id)
    return entry.owner_id==USER_ID

@login_manager.user_loader
def load_user(user_name):
    return User.query.get(user_name)

@app.route('/')
def initialize():
    db.create_all()
    logout_user()
    return redirect('/logout')

@app.route('/home')
def home():
    global USER_ID, post_per_page, current_page
    current_page = 1
    total_post = db.session.query(Entry).count()
    total_page = int(ceil(total_post / float(post_per_page))) #round up
    entry_id = []
    for i in range(1,post_per_page + 1):
        if ((current_page - 1) * post_per_page + i) < total_post:
            entry_id.append((current_page - 1)*post_per_page + i)

    entries = []
    authors = []
    for id in entry_id:
        entry = Entry.query.get(id)
        entries.append(entry)
        authors.append(User.query.get(entry.owner_id).user_name)
    if current_user.is_authenticated:  # already logged in
        loggedin = True
        username = User.query.get(USER_ID).user_name
    else:
        loggedin = False
        username = ''
    return render_template('index.html',
                           post_per_page=post_per_page,
                           current_page=current_page,
                           entry_id=entry_id,
                           entries=entries,
                           authors=authors,
                           loggedin=loggedin,
                           username=username,
                           total_page=total_page)
@app.route('/home/<int:page>')
def homepage(page):
    global USER_ID, post_per_page, current_page
    current_page = page
    total_post = db.session.query(Entry).count()
    total_page = int(ceil(total_post / float(post_per_page))) #round up
    print total_page
    entry_id = []
    for i in range(1,post_per_page + 1):
        if ((current_page - 1)*post_per_page + i) <= total_post:
            entry_id.append((current_page - 1)*post_per_page + i)
            print entry_id
    entries = []
    authors = []
    for id in entry_id:
        entry = Entry.query.get(id)
        entries.append(entry)
        authors.append(User.query.get(entry.owner_id).user_name)
    if current_user.is_authenticated:  # already logged in
        loggedin = True
        username = User.query.get(USER_ID).user_name
    else:
        loggedin = False
        username = ''
    return render_template('index.html',
                           post_per_page=post_per_page,
                           entry_id=entry_id,
                           entries=entries,
                           authors=authors,
                           loggedin=loggedin,
                           username=username,
                           current_page=current_page,
                           total_page=total_page)

@app.route('/login', methods=['GET','POST'])
def login():
    """Input > Querry > Login and Redirect to home/Re render with validation msg"""
    global USER_ID
    message = ''  # validation
    wrong = False # validation
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(user_name=username, password=md5(password.encode()).hexdigest()).first()
        if user:
            login_user(user=user)
            USER_ID = user.id
        else:
            wrong = True
            message = 'wrong username or password'
    if current_user.is_authenticated: # already logged in
        return redirect('/home')
    return render_template('login.html',
                           message=message,
                           wrong=wrong)

@app.route('/register',methods=['GET','POST'])
def register():
    """Input > Add to DB > Redirect to login"""
    wrong = False #validate duplication
    if request.method == 'POST':
        username = request.form['username']
        print username
        if User.query.filter_by(user_name=username).first() is None: # duplication
            password = request.form['password']
            db.session.add(User(username,password))
            db.session.commit()
            return redirect('/login')
        else:
            wrong = True
    return render_template('register.html',wrong=wrong)

@app.route('/logout')
def logout():
    global USER_ID
    logout_user()
    USER_ID = 0
    return redirect('/login')

@app.route('/<author>/account')
def account(author):
    user = User.query.filter_by(user_name=author).first()
    entries = Entry.query.filter_by(owner_id=user.id).all()
    if USER_ID != 0:
        loggedin = True
        username = User.query.get(USER_ID).user_name
    else:
        loggedin = False
        username = ''
    return render_template('account.html',
                           loggedin=loggedin,
                           username=username,
                           author=author,
                           entries=entries)

@app.route('/<username>/write')
@login_required
def write(username):
    """render the blog writting page"""
    if validate(username):
        return render_template('write.html',username=username)
    return 'WRITE Not Allowed'

@app.route('/<username>/written',methods=['POST'])
@login_required
def written(username):
    """post the created entry to db > redirect to the created entry"""
    global USER_ID
    if validate(username):
        title = request.form['title']
        content = request.form['content']
        entry = Entry(title,content,owner_id=USER_ID)
        db.session.add(entry)
        db.session.commit()
        link = url_for('post',entry_id=entry.id) #because redirect doesnt handle <var> syntax in url
        return redirect(link)
    else:
        return redirect('/logout') #only happens when wrong user type the url instead of using button

@app.route('/post/<entry_id>')
def post(entry_id):
    global USER_ID
    editable = False #to set active the edit button
    if own(entry_id):
        editable = True #can be edit if current user is owner
    entry = Entry.query.get(entry_id)
    author = User.query.get(entry.owner_id).user_name
    if USER_ID != 0:
        loggedin = True
        username = User.query.get(USER_ID).user_name
    else:
        loggedin = False
        username = ''
    return render_template('blogpost.html',
                           editable=editable,
                           title=entry.title,
                           content=entry.content,
                           entry_id=entry.id,
                           author=author,
                           loggedin=loggedin,
                           username=username)

@app.route('/post/<entry_id>/editpost',methods=['POST'])
@login_required
def edit(entry_id):
    if own(entry_id):
        entry = Entry.query.get(entry_id)
        return render_template('edit.html',
                               title=entry.title,
                               content=entry.content,
                               entry_id=entry.id)
    else:
        return 'EDIT Not Allowed'

@app.route('/post/<entry_id>/edited',methods=['POST'])
@login_required
def edited(entry_id):
    if own(entry_id):
        entry = Entry.query.get(entry_id)
        entry.title = request.form['title']
        entry.content = request.form['content']
        db.session.commit()
        link = url_for('post',entry_id=entry.id) #because redirect doesnt handle <var> syntax in url
        return redirect(link)
    else:
        return redirect('/logout')  # only happens when wrong user type the url instead of using button


if __name__ == '__main__':
    app.run(debug=True)

