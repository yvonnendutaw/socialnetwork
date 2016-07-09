from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, logout_user, login_required, current_user, login_user

import forms
import models

DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'codey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.select().where(
            models.User.id == int(userid)
        ).get()
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request"""
    g.db.close()
    return response

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
#        flash('you registered', "success")
        models.User.create_User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("you email or password doesn't match", "error")
            pass

        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
#                flash("you have been logged in")
                return redirect(url_for('post'))
            else:
                flash("you email or password doesn't match", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've loged out ! welcome back")
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
#        flash('Message posted!Thanks', "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@login_required
@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(
                models.User.username ** username).get()
        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


@app.route('/viewposts')
def index():
    """Home page view, shows a stream of all Social App posts"""
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_User(
            username='yvonne',
            email='yvonne@ymail.com',
            password='hello',
            admin=True

        )
    except ValueError:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)
