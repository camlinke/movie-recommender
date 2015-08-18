from app import app, db, login_manager
from flask import render_template, redirect, request, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user
from forms import SignUpForm, LoginForm
from models import User, Movie, Rating
from sqlalchemy.exc import IntegrityError
from delorean import Delorean
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('signup'))

@app.route('/')
def home():
    return render_template('home.html')

# User Specific Areas
@app.route('/rate')
@login_required
def rate():
    ratings = Rating.query.filter_by(user_id=current_user.id).all()
    r = [rating.movie_id for rating in ratings]
    movies = Movie.query.filter(~Movie.movie_id.in_(r)).limit(25).all()
    for m in movies:
        print m
    return render_template('rate.html', movies=movies)

@app.route('/rate_movie/<movie_id>/<rating>', methods=['POST'])
@login_required
def rate_move(movie_id, rating):
    try:
        print movie_id
        print rating
        date_time = str(int(Delorean().epoch()))
        r = Rating.query.filter_by(user_id=current_user.id).filter(Rating.movie_id == movie_id).first()
        print r
        if r:
            if rating == "0":
                db.session.delete(r)
                db.session.commit()
                return "success"
            else:
                r.rating = rating
                r.timestamp = date_time
        else:
            r = Rating(user_id = current_user.id,
                       movie_id = movie_id,
                       rating = rating,
                       timestamp = date_time)
        db.session.add(r)
        db.session.commit()
        print "successfull added/updated rating"
    except IntegrityError:
        db.session.rollback()
        print "error with rating"
    return "success"

@app.route('/recommendations')
@login_required
def recommendations():
    return render_template('recommendations.html')


# Signup, Login, Logout
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            if User.query.filter_by(email=form.email.data.lower()).first():
                print "User Exists"
                return render_template('signup.html', form=form)
            else:
                user = User(email=form.email.data, password=form.password.data)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('recommendations'))
        except IntegrityError:
            db.session.rollback()
            print "some sort of database error"
            return render_template('signup.html', form=form)
    else:
        print "form or post error"
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('recommendations'))
        else:
            print "user/username don't work"
            return render_template('login.html', form=form)
    else:
        print "form or post error"
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))