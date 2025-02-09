import os
import json
from app import app, db, DB_FILE, bcrypt
from models import *

def create_user():
    user = User(username="josh", password=bcrypt.generate_password_hash("password").decode("utf-8"))
    db.session.add(user)
    db.session.commit()

def load_data():
    with open("clubs.json") as f:
        clubs = json.load(f)
        for club_data in clubs:
            club = Club(name=club_data["name"], code=club_data["code"], description=club_data["description"])
            db.session.add(club)
            for tag_name in club_data.get("tags", []):
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                club.tags.append(tag)
    db.session.commit()

if __name__ == "__main__":
    LOCAL_DB_FILE = "instance/" + DB_FILE
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)
    with app.app_context():
        db.create_all()
        create_user()
        load_data()