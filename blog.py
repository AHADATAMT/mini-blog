from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user, login_url

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login_b'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


db.create_all()


@app.route("/")
def index():
    return redirect(url_for('posts'))


@app.route("/posts")
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)


@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    users = User.query.all()
    if request.method == 'POST':
        isError = validate_create_form(request.form)
        if not isError["error"]:
            post = Post(
                title=request.form['title'],
                body=request.form['body'],
                user_id=request.form['author']
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('posts'))
        else:
            flash(isError["msg"], isError["category"])

    return render_template('create_form.html', authors=users)


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', user=current_user.username)


@app.route('/login_b', methods=['POST', 'GET'])
def login_b():
    error = None
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        user = User.query.filter_by(email=user_email).first()
        if(user is not None and user.check_password(user_password)):
            flash('Hi! ' + user.username, 'alert-success')
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('profile'))
        else:
            flash('Wrong Email/Password', 'alert-danger')

    return render_template('login.html', error=error)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        user_email = request.form['email']
        user_password = request.form['password']
        user = User(username=username, email=user_email)
        user.set_password(user_password)
        db.session.add(user)
        db.session.commit()
        if user is not None:
            return redirect(url_for('login_b'))

    return render_template('signup.html', error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout success', 'alert-success')
    return redirect(url_for('login_b'))


@app.route("/<username>/posts")
def user_post(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "This username isn't available"
    posts = Post.query.filter_by(user_id=user.id).first()
    print(posts)
    if posts is None:
        return "This username doesn't have any post"

    userposts = []
    for post in user.posts:
        userposts.append({
            "id": post.id,
            "title": post.title,
            "body": post.body,
        })
    userposts = json.dumps(userposts)
    # userposts = [
    #     {
    #         "id": post['id'] for post in user.posts,
    #     }
    # ]
    return userposts


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# verify input fields


def validate_create_form(form):
    if len(form['title']) == 0:
        return {"error": True, "msg": "title cannot be blank", "category": "error-title"}
    if len(form['body']) == 0:
        return {"error": True, "msg": "content cannot be blank", "category": "error-content"}

    return {"error": False}


if __name__ == '__main__':
    app.run(environment="development")
