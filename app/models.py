from app import db
from app import bcrypt
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)
    pw_hash = db.Column(db.String())

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = self.set_password_hash(password)

    def set_password_hash(self, password):
        return bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pw_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email %r>' % (self.email)

class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String())
    name = db.Column(db.String())
    year = db.Column(db.Integer())

    def __init__(self, name, movie_id, year):
        self.name = name
        self.movie_id = movie_id
        self.year = year

    def __repr__(self):
        return '<name %r>' % (self.name)

class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String())
    movie_id = db.Column(db.String())

    def __init__(self, genre_name, movie_id):
        self.genre_name = genre_name
        self.movie_id = movie_id

    def __repr__(self):
        return '<genre_name %r>' % (self.genre_name)

class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    movie_lense_user_id = db.Column(db.String(), index=True)
    movie_id = db.Column(db.String(), nullable=False, index=True)
    rating = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.String(), nullable=False)

    def __init__(self, movie_id, rating, timestamp, user_id=None, movie_lense_user_id=None):
        self.movie_id = movie_id
        self.rating = rating
        self.timestamp = timestamp
        self.user_id = user_id
        self.movie_lense_user_id = movie_lense_user_id

    def __repr__(self):
        return '<movie_id %r>' % (self.movie_id)
