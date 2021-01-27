from app import manager, db
from app.catalog.models import *


# init - python manage.py db init
# make migration - python manage.py db migrate
# apply migration - python manage.py db upgrade
if __name__ == '__main__':
    manager.run()