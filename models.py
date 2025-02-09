from datetime import datetime, UTC
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    favorites = db.relationship('Club', secondary='favorite_club', back_populates='favorited_by')
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True, default="")
    rating = db.Column(db.Float, nullable=True, default=None)
    favorite_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    reviews = db.relationship('Review', back_populates='club', cascade='all, delete-orphan')
    favorited_by = db.relationship('User', secondary='favorite_club', back_populates='favorites')
    tags = db.relationship('Tag', secondary='club_tag', back_populates='clubs')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    club = db.relationship('Club', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')
    __table_args__ = (
        db.CheckConstraint('rating >= 1 and rating <= 5 and rating = CAST(rating AS INTEGER)', 
                         name='check_rating_range_and_type'),
    )

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    clubs = db.relationship('Club', secondary='club_tag', back_populates='tags')

class ClubTag(db.Model):
    club_id = db.Column(db.Integer, db.ForeignKey('club.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

class FavoriteClub(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))