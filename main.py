from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'GET' and request.args.get('id') == None:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a blog!", blogs=blogs)
    else:   
        id = request.args.get('id')
        blogs = Blog.query.get(id)
        return render_template('individualblog.html', title="Build a blog!", blogs=blogs)

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