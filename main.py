from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

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
    owner_id = db.Column(db.Integer)
    #need to link the foreign key owner_id somehow

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.Column(db.Integer)
    #note in 'add user class' it requres we add this blogs entry, as well as in blog class.

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        redirect('/login')
    #Do we need /blog to be in the allowed fields if they are not logged in?

@app.route('/')
def index():
    #It states in 'add navigation' that index must have a list of all usernames that go to individuial blogs when clicked
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - Validate user data
        #After validation, should redirect to newpost page

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            return "<h1>Duplicate user</h1>"
            #need to turn this into a flash message with redirect back to /signup

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
        else:
            return '<h1>Error!</h1>'
            #need to turn this into a flash message and redirect back to login
            #Use cases require it to distinguish between 'user doesn't exist' and 'password incorrect'
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['email']
    return redirect('/blog')
    #note this has to be a post request per rubrick, may need to add a form on the nav to make it so

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    #i'm just using the old blog.html template for this moment, needs updating
    #Per functionality check, when they visit /blog it lists all blogs by all users
    #Per functionality check, when clicking a link on any entry it takes them to that individual page
    if request.method == 'GET' and request.args.get('id') == None:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Blogz!", blogs=blogs)
    else:   
        id = request.args.get('id')
        blogs = Blog.query.get(id)
        return render_template('individualblog.html', title="Blogz!", blogs=blogs)
        #This is the 'single post page' request. Need to add one for 'single user, all posts' by getting the user_ids. 
        #Last section of rubrick says to use query params 'user' and 'id'

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']

        if not title_name or not body_name:
            flash('Please enter both a title and body text')
            return render_template('newpost.html', title="Add Post", title_name = title_name, body_name = body_name)

        new_entry = Blog(title_name, body_name)
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_entry.id)) 
    
    return render_template('newpost.html', title="Add Post")

if __name__ == '__main__':
    app.run()