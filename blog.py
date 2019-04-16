from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(80))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


db.create_all()


@app.route("/")
def index():
    return redirect(url_for('posts'))


@app.route("/posts")
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        isError = validate_create_form(request.form)
        if not isError["error"]:
            post = Post(
                title=request.form['title'],
                body=request.form['body'],
                author_name=request.form['author']
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('posts'))
        else:
            flash(isError["msg"], isError["category"])

    return render_template('create_form.html', last=request.form)


def validate_create_form(form):
    if len(form['title']) == 0:
        return {"error": True, "msg": "title cannot be blank", "category": "error-title"}
    if len(form['body']) == 0:
        return {"error": True, "msg": "content cannot be blank", "category": "error-content"}

    return {"error": False}

if __name__ == '__main__': 
    app.run(environment="development")