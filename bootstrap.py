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
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
