
"""
view related to the userZ:

1. register
2. login
3. logout
4. account (update UserForm)
5. user's list of blog posts

"""
from flask_login.login_manager import LoginManager
from flask_login.mixins import UserMixin
from wtforms import meta
from company_blog.users.forms import RegsitrationForm, LoginForm, UpdateUserForm
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from company_blog import db
from company_blog.models import User, BlogPost
from company_blog.users.picture_handler import add_profile_pic

#register blueprint
users = Blueprint('users', __name__)

#login
@users.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        #query the user from the db to get an object of the User class
        user = User.query.filter_by(email=form.email.data).first() #email is unique

        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash("Successfully logged in!")

            #this gets the url that the user was actually trying to get to before being redirected to the login page.
            next = request.args.get('next')

            if next == None or next[0] == "/":
                next = url_for("core.index")

            return redirect(next)

    return render_template("login.html", form=form)

 
#logout
@users.route("/logout")
def logout():
    
    logout_user() #default flask method
    return redirect(url_for('core.index'))

#register user (includes GET AND POST methods since it has form input)
@users.route("/register", methods=["GET", "POST"])
def register():
    
    form = RegsitrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, 
        username=form.username.data, 
        password=form.password.data
        )

        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering!")

        return redirect(url_for('users.login'))
    
    return render_template('register.html', form=form)


#account (update Userform)
@users.route("/account", methods=["POST", "GET"])
@login_required
def account():

    form = UpdateUserForm()
    if form.validate_on_submit():

        #if user uploads a pic
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash("User Account Updated!")

        return redirect(url_for('users.account')) #or redirect('core.index')

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/')
    return render_template("account.html", profile_image=profile_image, form=form)

#user posts
@users.route('/<username>')
def user_posts(username):

    #paginate user blog posts
    page = request.args.get('page', 1, type=int)

    #get the first user (username is unique, should only be 1). if not found, return 404
    user = User.query.filter_by(username=username).first_or_404()

    #backref to the BlogPost db class to the users is author which is used here.  
    blog_posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.date.desc()).paginate(page=page, per_page=5)

    return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user)