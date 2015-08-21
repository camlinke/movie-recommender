from app import app, db, login_manager
from flask import render_template, redirect, request, url_for, g
from flask.ext.login import login_user, logout_user, login_required, current_user
from forms import SignUpForm, LoginForm
from models import User, Movie, Rating
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
from delorean import Delorean
import json
import random
import subprocess


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('signup'))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def home():
    return render_template('home.html')

# User Specific Areas
@app.route('/rate')
@login_required
def rate():
    ratings = Rating.query.filter_by(user_id=current_user.id).all()
    r = [rating.movie_id for rating in ratings]
    count = Movie.query.count()
    random_num = random.randint(1, 100)
    random_range = [x for x in xrange(count) if x % random_num == 0]
    # rand_num = random.randrange(50, count)
    # random_range = range(rand_num-50, rand_num)
    movies = Movie.query.filter(~Movie.movie_id.in_(r)).filter(Movie.id.in_(random_range)).limit(25).all()
    random.shuffle(movies)
    return render_template('rate.html', movies=movies)

@app.route('/rate_movie/<movie_id>/<rating>', methods=['POST'])
@login_required
def rate_movie(movie_id, rating):
    try:
        date_time = str(int(Delorean().epoch()))
        r = Rating.query.filter_by(user_id=current_user.id).filter(Rating.movie_id == movie_id).first()
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
    u = User.query.filter_by(id=current_user.id).first()
    ratings = Rating.query.filter_by(user_id=current_user.id).all()
    movies = []
    if u.recommendations:
        ids = [x for x in json.loads(u.recommendations)]
        print u.recommendations
        r = [rating.movie_id for rating in ratings]
        movies = Movie.query.filter(Movie.movie_id.in_(ids)).filter(~Movie.movie_id.in_(r)).limit(25)
    elif len(ratings) < 10:
        return redirect(url_for('rate'))
    else:
        subprocess.call(["pyspark", "engine/engine.py", "small", "id:{}".format(current_user.id)])
    return render_template('recommendations.html', movies=movies)


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