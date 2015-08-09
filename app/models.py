from app import db
from app import bcrypt

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
    name = db.Column(db.String())
    genres = db.relationship('Genre', backref='movies')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name %r>' % (self.name)

class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(), unique=True)
    movie_id = db.Column(db.Integer())

    def __init__(self, genre_name, movie_id):
        self.genre_name = genre_name
        self.movie_id = movie_id

    def __repr__(self):
        return '<genre_name %r>' % (self.genre_name)