import os
from flask import Flask

"""
    This files provides function to create server application 
    along with database connection
"""
def create_app(test_config=None):
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET_KEY'],
        DATABASE=os.path.join(app.instance_path, 'socialize.sqlite'),
        IMAGE_FOLDER=os.path.join(BASEDIR, "static", os.environ['UPLOAD_IMAGE_FOLDER']),
        THUMBNAIL_FOLDER=os.path.join(BASEDIR, "static", os.environ['THUMBNAIL_FOLDER']),
        ALLOWED_EXTENSIONS=os.environ['ALLOWED_EXTENSIONS'].split(',')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # database initialization 
    from . import db
    db.init_app(app)
    
    # authentication blueprint 
    from . import auth
    app.register_blueprint(auth.bp)
    
    # root application blueprint
    from . import socialize
    app.register_blueprint(socialize.bp)

    app.add_url_rule('/', endpoint='index')

    return app

