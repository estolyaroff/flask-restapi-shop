from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)
api = Api(app)
from app.catalog.views import catalog

app.register_blueprint(catalog)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
