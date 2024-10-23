from flask import Blueprint, render_template, request, redirect, url_for
from flask import flash 
from app.forms import LoginForm, RegistrationForm, BlogForm
from app.models import db, User, Task, BlogPost
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')
from flask import flash

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful for {}'.format(form.username.data), 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)



@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.home'))


@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    Task.query.filter_by(user_id=user.id).delete()  # Delete user's tasks
    db.session.delete(user)  # Delete user
    db.session.commit()
    logout_user()
    flash('Your account has been deleted.', 'info')
    return redirect(url_for('main.home'))


@main.route('/blogs')
@login_required
def view_blogs():
    posts = BlogPost.query.all()
    return render_template('view_blogs.html', posts=posts)

@main.route('/blogs/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    form = BlogForm()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your blog post has been created!', 'success')
        return redirect(url_for('main.view_blogs'))
    return render_template('create_blog.html', form=form)

@main.route('/blogs/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to update this post.', 'danger')
        return redirect(url_for('main.view_blogs'))
    form = BlogForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your blog post has been updated!', 'success')
        return redirect(url_for('main.view_blogs'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_blog.html', form=form)

@main.route('/blogs/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('main.view_blogs'))
    db.session.delete(post)
    db.session.commit()
    flash('Your blog post has been deleted!', 'info')
    return redirect(url_for('main.view_blogs'))
