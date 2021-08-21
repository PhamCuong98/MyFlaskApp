from config import *
from flask import Flask, config
import flask_sqlalchemy

from models import db
from config import *

def create_app(ENV):
    app = Flask(__name__)
    
    if ENV == "DEV":
        #app.debug(True)
        app.config['SQLALCHEMY_DATABASE_URI']= SQLALCHEMY_DATABASE_URI_DEV
        """ Command terminal
            from init import db
            db.create_all()
            db.close()
        """ 
    elif ENV == "PRODUCT":
        #app.debug(False)
        app.config['SQLALCHEMY_DATABASE_URI']= SQLALCHEMY_DATABASE_URL
        
        """ Command terminal
        heroku run python
        from init import db
        db.create_all()
        """
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.app_context().push()
    app.secret_key = b'phamcuong1812'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['RESULT_FOLDER'] = RESULT_FOLDER
    db.init_app(app)
    db.create_all()
    return app
