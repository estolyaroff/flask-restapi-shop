from app import manager, db
from app.catalog.models import *


# для снимка базы - python manage.py db init
#
if __name__ == '__main__':
    manager.run()