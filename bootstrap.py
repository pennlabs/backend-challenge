import os
from app import db, DB_FILE

def create_user():
    print("TODO: Create a user called josh")

def load_data():
    from models import *
    print("TODO: Load in clubs.json to the database.")



# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    LOCAL_DB_FILE = "instance/" + DB_FILE
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)

    with app.app_context():
        db.create_all()
    create_user()
    load_data()
