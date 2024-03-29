from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self, email, password):
        self.email = email
        self.password = password

def is_blank(string):
    len(string) == 0

def length_valid(string):
    if len(string) > 20 or len(string) < 3:
        return False
    else:
        return True

def contains_spaces(string):
    spaces = 0
    for c in string:
        if c == ' ':
            spaces = spaces + 1
    return spaces > 0

def one_at(string):
    at = 0
    for c in string:
        if c == '@':
            at = at + 1
    return at == 1

def one_dot(string):
    dot = 0
    for c in string:
        if c == '.':
            dot = dot + 1
    return dot == 1

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
   users =  User.query.all()
   return render_template('index.html', users = users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    password_error = ''
    verify_error = ''
    email_error = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if is_blank(password):
            password_error = "Password must not be blank"
        elif length_valid(password) == False or contains_spaces(password) == True:
            password_error = "Password must be between 3 and 20 characters and must not contain spaces"

        if is_blank(verify):
            verify_error = "Password must not be blank"
        elif length_valid(verify) == False or contains_spaces(verify) == True:
            verify_error = "Password must be between 3 and 20 characters and must not contain spaces"

        if password != verify:
            password_error: "Passwords must Match"
            verify_error = "Passwords must match"

        if length_valid(email) == False or contains_spaces(email) == True or one_at(email) == False or one_dot(email) == False:
            email_error = "Email must be between 3 and 20 characters, must not contain spaces, and may only contain one at and one dot"

        if not password_error and not verify_error and not email_error:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/')
            else:
                email_error = "Duplicate email! Please use another"
                return render_template('signup.html', password_error = password_error, verify_error = verify_error, email_error = email_error, password='', verify='', email=email)         
            
            return redirect('/newpost')

        else: 
            return render_template('signup.html', password_error = password_error, verify_error = verify_error, email_error = email_error, password='', verify='', email=email)
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        if not user:
            flash("Invalid username")
            return redirect('/login')
        if user and user.password != password:
            flash("Invalid password")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['email']
    flash('Logged out')
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('id') == None and request.args.get('user') == None:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Blogz!", blogs=blogs)
    elif request.args.get('id') != None:   
        id = request.args.get('id')
        blogs = Blog.query.get(id)
        return render_template('individualblog.html', title="Blogz!", blogs=blogs)
    elif request.args.get('user') != None:
        user_id = request.args.get('user')
        blogz = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('singleuser.html', title="Blogz!", blogz=blogz)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        owner = User.query.filter_by(email = session['email']).first()
        owner_id = owner.id

        if not title_name or not body_name:
            flash('Please enter both a title and body text')
            return render_template('newpost.html', title="Add Post", title_name = title_name, body_name = body_name)

        new_entry = Blog(title_name, body_name, owner_id)
        db.session.add(new_entry)
        db.session.commit()

        return redirect('/blog?id={}'.format(new_entry.id)) 
    
    return render_template('newpost.html', title="Add Post")

if __name__ == '__main__':
    app.run()