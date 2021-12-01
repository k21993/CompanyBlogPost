import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


#instantiate app
app = Flask(__name__)

#secret key
app.config["SECRET_KEY"] = 'some_secret'

#setup database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Migrate(app, db)

#setup login configurations
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "users.login"

#register blueprints
#moved imports here as these imports on top were causing circular import issues while registering db
from company_blog.core.views import core
from company_blog.error_pages.handlers import error_pages
from company_blog.users.views import users
from company_blog.blog_posts.views import blog_posts

app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(blog_posts)