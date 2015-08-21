from pyspark import SparkContext
from pyspark.mllib.recommendation import ALS
from pyspark.mllib.linalg import Vectors
# from app.models import User, Rating
# from app import app, db
import numpy as np
import scipy.sparse as sps
import sys
import os
import csv
import math
import json
import requests

sc = SparkContext()

small_ratings = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest-small/ratings.csv')
large_ratings = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest/ratings.csv')

small_movies = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest-small/movies.csv')
large_movies = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest/ratings.csv')
# app.config.from_object(os.environ['APP_SETTINGS'])

# ratingsRDD = rawRatings.map

# class RatingEngine:
    
#     def __init__(self, ratings_rdd, user_ratings):
#         self.ratings_rdd = ratings_rdd
#         self.user_ratings = user_ratings

#     # Cosine Similarity for Individual Recommendations
#     def cosine_similarity(self, user1, user2):
#         """ Takes in two Dense Vectors of user's Recommendations and
#             returns the cosine similarity between the two.
#         """
#         return user1.dot(user2) / (math.sqrt(user1.dot(user1)) * math.sqrt(user2.dot(user2)))

#     # Create sparse vectors grouped by usersId
#     # movies_length = ratingsRDD.count()

#     def similarities_for_user(self, user_id, crossRDD):
#         """
#         Takes in a user_id and and RDD of crossed user_ids with that user
#         Returns an array of the top 10 users who are most similar to a 
#         """
#         similarities = (crossRDD
#                         .filter(lambda x: x[0][0] == user_id)
#                         .map(lambda x: (x[0][0], x[1][0], self.cosine_similarity(x[0][1], x[1][1]))))
#         return (similarities
#                 .filter(lambda x: x[0] == int(user_id)))

#     def similarities_for_vector(self, user_id, user_data_rdd, user_ids_with_ratings_rdd):
#         """
#         Takes in a tuple of form (user_id, sparse_vector_of_ratings) and combines it with existing
#         rating rdd. and returns cosine similarities for that user with existing users
#         sorted higheset to lowest
#         """
#         cross_rdd = user_data_rdd.cartesian(user_ids_with_ratings_rdd)
#         return self.similarities_for_user(user_id, cross_rdd)

#     def create_user_with_sparse_ratings(self, user_id, ratings, movies_length):
#         """
#         Creates a rdd with (user_id, sparse_vector_of_ratings) from a user_id and array of
#         (movie_id, rating) tuples.
#         """
#         return sc.parallelize([(user_id, Vectors.sparse(movies_length, ratings))])

#     def create_id_rating_tuples(self, scalar, vector):
#         """
#         Takes in scalar and sparse vector multiplies them together and returns
#         (movie_id, rating) tuple
#         """
#         updated_ratings = vector.toArray().dot(scalar)
#         return [(i, rating) for i, rating in enumerate(updated_ratings) if rating != 0]

#     def create_most_similar_for_user_rdd(self, user_ratings, user_ids_with_ratings_rdd, movies_length):
#         return self.similarities_for_vector(0, self.create_user_with_sparse_ratings(0, user_ratings, movies_length), user_ids_with_ratings_rdd)

#     def create_similar_users_and_similarity_rdd(self, mostSimilarForUserRDD):
#         return mostSimilarForUserRDD.sortBy(lambda x: -x[2]).map(lambda x: (x[1], x[2]))

#     def get_top_movies_for_user(self):
#         movies_length = self.ratings_rdd.map(lambda x: x[1]).max() + 1
#         user_ids_with_ratings_rdd = (self.ratings_rdd
#                                      .map(lambda (user_id, movie_id, rating): (user_id, [(movie_id, rating)]))
#                                      .reduceByKey(lambda a, b: a + b)
#                                      .map(lambda x: (x[0], Vectors.sparse(movies_length, x[1]))))
#         user_seen_movies_list = [x[0] for x in self.user_ratings]
#         most_similar_for_user_rdd = self.create_most_similar_for_user_rdd(self.user_ratings, user_ids_with_ratings_rdd, movies_length)
#         similar_users_and_similarity_rdd = self.create_similar_users_and_similarity_rdd(most_similar_for_user_rdd)
#         top_movies_for_user = (user_ids_with_ratings_rdd
#                            .join(similar_users_and_similarity_rdd)
#                            .flatMap(lambda x: self.create_id_rating_tuples(x[1][1], x[1][0]))
#                            .reduceByKey(lambda a, b: max(a, b))
#                            .filter(lambda x: x[0] not in user_seen_movies_list)
#                            .takeOrdered(50, lambda x: -x[1]))
#         return top_movies_for_user



num_partitions = 2
user_id = None

if len(sys.argv) > 0:
    for arg in sys.argv:
        if arg == "large":
            raw_ratings = sc.textFile(large_ratings).repartition(num_partitions)
            raw_movies = sc.textFile(large_movies)
        if arg == "small":
            raw_ratings = sc.textFile(small_ratings).repartition(num_partitions)
            raw_movies = sc.textFile(small_movies)
        if arg[:3] == "id:":
            user_id = arg[3:]
else:
    raw_ratings = sc.textFile(small_ratings).repartition(num_partitions)
    raw_movies = sc.textFile(small_movies)

def get_ratings_tuple(entry):
    items = entry.split(',')
    return int(items[0]), int(items[1]), float(items[2])

def get_movie_tuple(entry):
    items = entry.split(',')
    return int(items[0]), items[1]

def get_counts_and_averages(IDandRatingsTuple):
    id = IDandRatingsTuple[0]
    length = len(IDandRatingsTuple[1])
    average = 1.0 * sum(IDandRatingsTuple[1]) / length
    return (id, (length, average))

def compute_error(predictedRDD, actualRDD):
    # Transform predictedRDD into the tuples of the form ((UserID, MovieID), Rating)
    predictedReformattedRDD = predictedRDD.map(lambda x: ((x[0], x[1]), x[2]))

    # Transform actualRDD into the tuples of the form ((UserID, MovieID), Rating)
    actualReformattedRDD = actualRDD.map(lambda x: ((x[0], x[1]), x[2]))

    # Compute the squared error for each matching entry
    squaredErrorsRDD = (predictedReformattedRDD
                        .join(actualReformattedRDD)
                        .map(lambda x: (x[0], (math.pow((x[1][0]-x[1][1]), 2)))))

    totalError = sum(squaredErrorsRDD.values().take(squaredErrorsRDD.count()))

    # Count the number of entries for which you computed the total squared error
    numRatings = squaredErrorsRDD.count()

    # Compute the RSME
    return math.sqrt(totalError / numRatings)

header = raw_ratings.first()
ratingsRDD = raw_ratings.filter(lambda line: line != header).map(get_ratings_tuple).cache()

header = raw_movies.first()
moviesRDD = raw_movies.filter(lambda line: line != header).map(get_movie_tuple).cache()
movieIDsWithRatingsRDD = (ratingsRDD
                          .map(lambda x: (x[1], x[2]))
                          .groupByKey())
movieIDsWithAvgRatingsRDD = movieIDsWithRatingsRDD.map(get_counts_and_averages)
movieNameWithAvgRatingsRDD = (moviesRDD
                              .join(movieIDsWithAvgRatingsRDD)
                              .map(lambda x: (x[1][1][1], x[1][0], x[1][1][0])))
# print movieNameWithAvgRatingsRDD.filter(lambda x: x[2] > 150).takeOrdered(3, lambda x: -x[0])

# trainingRDD, validationRDD, testRDD = ratingsRDD.randomSplit([6, 2, 2], seed=0L)

# # ALS Prediction
# validationForPredictRDD = validationRDD.map(lambda x: (x[0], x[1]))

# seed = 5L
# iterations = 5
# regularizationParameter = 0.1
# ranks = [4, 8, 12]
# errors = [0, 0, 0]
# err = 0
# tolerance = 0.02
# error = None

# minError = float('inf')
# bestRank = -1
# bestIteration = -1

# for rank in ranks:
#     model = ALS.train(trainingRDD, rank, seed=seed, iterations=iterations, lambda_=regularizationParameter)
#     predictedRatingsRDD = model.predictAll(validationForPredictRDD)
#     error = compute_error(predictedRatingsRDD, validationRDD)
#     errors[err] = error
#     err += 1
#     print 'For rank %s the RMSE is %s' % (rank, error)
#     if error < minError:
#         minError = error
#         bestRank = rank

# myModel = ALS.train(trainingRDD, bestRank, seed=seed, iterations=iterations,
#                       lambda_=regularizationParameter)
# testForPredictingRDD = testRDD.map(lambda x: (x[0], x[1]))
# predictedTestRDD = myModel.predictAll(testForPredictingRDD)

# testRMSE = compute_error(testRDD, predictedTestRDD)

# print 'The model had a RMSE on the test set of %s' % testRMSE


fake_user_ratings = [(1, 5), (7, 3), (173, 2), (99, 1), (88, 5), (288, 5), (405, 3), (296, 5), (47, 5), (1432, 4)]
user_seen_movies_list = [x[0] for x in fake_user_ratings]
# mostSimilarForUserRDD = similarities_for_vector(0, create_user_with_sparse_ratings(0, fake_user_ratings))

# movie recommendataion score = similarity_rating * user_movie rating
# create rdd of movie_id recommendation score

# mostSimilarForUserRDD = create_most_similar_for_user_rdd(fake_user_ratings)
# similarUsersAndSimilarityRDD = create_similar_users_and_similarity_rdd(mostSimilarForUserRDD)

# print get_most_similar_for_user(userIDsWithRatingsRDD, similarUsersAndSimilarityRDD, user_seen_movies_list)
# print userIDsWithRatingsRDD.map(lambda x: x[1]).map()

# crossUsers = userIDsWithRatingsRDD.cartesian(userIDsWithRatingsRDD).filter(lambda x: x[0] != x[1]).cache()

# Cosine Similarity for Individual Recommendations
def cosine_similarity(user1, user2):
    """ Takes in two Dense Vectors of user's Recommendations and
        returns the cosine similarity between the two.
    """
    return user1.dot(user2) / (math.sqrt(user1.dot(user1)) * math.sqrt(user2.dot(user2)))

# Create sparse vectors grouped by usersId
# movies_length = ratingsRDD.count()

def similarities_for_user(user_id, crossRDD):
    """
    Takes in a user_id and and RDD of crossed user_ids with that user
    Returns an array of the top 10 users who are most similar to a 
    """
    similarities = (crossRDD
                    .filter(lambda x: x[0][0] == user_id)
                    .map(lambda x: (x[0][0], x[1][0], cosine_similarity(x[0][1], x[1][1]))))
    return (similarities
            .filter(lambda x: x[0] == int(user_id)))

def similarities_for_vector(user_id, user_data_rdd, user_ids_with_ratings_rdd):
    """
    Takes in a tuple of form (user_id, sparse_vector_of_ratings) and combines it with existing
    rating rdd. and returns cosine similarities for that user with existing users
    sorted higheset to lowest
    """
    cross_rdd = user_data_rdd.cartesian(user_ids_with_ratings_rdd)
    return similarities_for_user(user_id, cross_rdd)

def create_user_with_sparse_ratings(user_id, ratings, movies_length):
    """
    Creates a rdd with (user_id, sparse_vector_of_ratings) from a user_id and array of
    (movie_id, rating) tuples.
    """
    return sc.parallelize([(user_id, Vectors.sparse(movies_length, ratings))])

def create_id_rating_tuples(scalar, vector):
    """
    Takes in scalar and sparse vector multiplies them together and returns
    (movie_id, rating) tuple
    """
    updated_ratings = vector.toArray().dot(scalar)
    return [(i, rating) for i, rating in enumerate(updated_ratings) if rating != 0]

def create_most_similar_for_user_rdd(user_ratings, user_ids_with_ratings_rdd, movies_length):
    return similarities_for_vector(0, create_user_with_sparse_ratings(0, user_ratings, movies_length), user_ids_with_ratings_rdd)

def create_similar_users_and_similarity_rdd(mostSimilarForUserRDD):
    return mostSimilarForUserRDD.sortBy(lambda x: -x[2]).map(lambda x: (x[1], x[2]))

def get_top_movies_for_user(user_ratings=fake_user_ratings, ratings_rdd=ratingsRDD):
    movies_length = ratings_rdd.map(lambda x: x[1]).max() + 1
    user_ids_with_ratings_rdd = (ratings_rdd
                                 .map(lambda (user_id, movie_id, rating): (user_id, [(movie_id, rating)]))
                                 .reduceByKey(lambda a, b: a + b)
                                 .map(lambda x: (x[0], Vectors.sparse(movies_length, x[1]))))
    user_seen_movies_list = [x[0] for x in user_ratings]
    most_similar_for_user_rdd = create_most_similar_for_user_rdd(user_ratings, user_ids_with_ratings_rdd, movies_length)
    similar_users_and_similarity_rdd = create_similar_users_and_similarity_rdd(most_similar_for_user_rdd)
    top_movies_for_user = (user_ids_with_ratings_rdd
                       .join(similar_users_and_similarity_rdd)
                       .flatMap(lambda x: create_id_rating_tuples(x[1][1], x[1][0]))
                       .reduceByKey(lambda a, b: max(a, b))
                       .filter(lambda x: x[0] not in user_seen_movies_list)
                       .takeOrdered(50, lambda x: -x[1]))
    return top_movies_for_user


# print get_top_movies_for_user(fake_user_ratings, ratingsRDD)


# try:
#     if user_id != None:
#         user = User.query.filter_by(id=user_id).first()
#         if user:
#             ratings = Rating.query.filter(Rating.user_id == user.id).all()
#             user_ratings = [(int(rating.movie_id), int(rating.rating)) for rating in ratings]
#             recommendations = {key: value for key, value in get_top_movies_for_user(user_ratings=user_ratings)}
#             user.recommendations = json.dumps(recommendations)
#             db.session.add(user)
#             db.session.commit()
# except Exception as e:
#     print e
#     print "didn't work"

ratings = requests.get('http://localhost:5000/api/users/{}'.format(user_id)).json()['ratings']

user_ratings = [(int(id), int(rating)) for id, rating in ratings]
recommendations = {key: value for key, value in get_top_movies_for_user(user_ratings=user_ratings)}
r = requests.post('http://localhost:5000/api/users/{}'.format(user_id), data=json.dumps({"recommendations" : recommendations}))
print r.text





