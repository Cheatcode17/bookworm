from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail,Message
#istantiate 



csrf = CSRFProtect()
mail = Mail()
def create_app():
    from bookapp.models import db
    app = Flask(__name__,instance_relative_config=True)

    
#load the routes here
    app.config.from_pyfile("config.py",silent=True)
    db.init_app(app)
    csrf.init_app(app)
    migrate = Migrate(app,db)
    return app
app = create_app()
from bookapp import admin_routes,user_routes
from bookapp.forms import *