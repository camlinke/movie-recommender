from app import db
from app.models import Movie, Genre, Rating
from flask.ext.script import Command
import csv
import os


class MovieImport(Command):
    def run(self):
        # if os.environ["APP_SETTINGS"] = "config.ProductionConfig"
        if os.environ["APP_SETTINGS"] == "config.DevelopmentConfig":
            file_path = "{}/ml-latest/movies.csv"\
                        .format(os.environ["MOVIE_DATA_LOCATION"])
        with open(file_path, "r") as movie_file:
            movie_reader = csv.reader(movie_file, delimiter=',')
            # Skip the header
            next(movie_reader, None)
            for movie in movie_reader:
                try:
                    movie_id = movie[0]

                    # Deal with movies that are enclosed in quotes
                    if movie[1].strip()[0] == '"':
                        movie_name = movie[1].strip()[1:-8]
                        movie_year = movie[1].strip()[-6:-2]
                    else:
                        movie_name = movie[1].strip()[:-7]
                        movie_year = int(movie[1].strip()[-5:-1])

                    genres = movie[2].split("|")

                    if Movie.query.filter_by(movie_id=movie_id).first():
                        continue
                    m = Movie(movie_id=movie_id,
                              name=movie_name,
                              year=movie_year)
                    db.session.add(m)

                    if genres[0] != '(no genres listed)':
                        for genre in genres:
                            movie_genre = Genre(genre_name=genre,
                                                movie_id=movie_id)
                            db.session.add(movie_genre)

                    db.session.commit()

                except Exception as e:
                    print movie[1]
                    db.session.rollback()
                    print "error ", e

            # I wrote this to find what movies didn't have
            # dates so I could fix them by hand
            # for movie in movie_reader:
            #     if movie[1].strip()[-1] != ")":
            #         print movie[1]
            #         continue


class RatingsImport(Command):
    def run(self):
        with open("{}/ml-latest/ratings.csv".format(
                  os.environ["MOVIE_DATA_LOCATION"]), "r") as ratings_file:
            ratings_reader = csv.reader(ratings_file, delimiter=',')
            next(ratings_reader, None)

            for rating in ratings_reader:
                try:
                    movie_lense_user_id = rating[0]
                    movie_id = rating[1]
                    movie_rating = rating[2]
                    timestamp = rating[3]
                    if Rating.query.filter(Rating.movie_id == movie_id)\
                                   .filter(Rating.movie_lense_user_id == movie_lense_user_id)\
                                   .first():
                        continue

                    r = Rating(movie_id=movie_id,
                               rating=movie_rating,
                               timestamp=timestamp,
                               movie_lense_user_id=movie_lense_user_id)
                    db.session.add(r)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print rating
                    print "error ", e


class ImportURLs(Command):
    def run(self):
        with open("{}/ml-latest/links.csv".format(
                  os.environ["MOVIE_DATA_LOCATION"]), "r") as url_file:
            url_reader = csv.reader(url_file, delimiter=',')
            next(url_reader, None)
            for movie_id, imdb_id, tmdb_id in url_reader:
                try:
                    movie = Movie.query\
                                 .filter(Movie.movie_id == movie_id).first()
                    if movie:
                        movie.movie_id = movie_id
                        movie.imdb_id = imdb_id
                        movie.tmdb_id = tmdb_id
                        db.session.add(movie)
                        db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print "error ", e
