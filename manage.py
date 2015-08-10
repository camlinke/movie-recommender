from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import os
from data_importer import MovieImport, RatingsImport

from app import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

manager.add_command('import_movies', MovieImport)
manager.add_command('import_ratings', RatingsImport)

if __name__ == '__main__':
    manager.run()
