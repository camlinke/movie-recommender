from pyspark import SparkContext
from pyspark.mllib.recommendation import ALS
from pyspark.mllib.linalg import Vectors
import numpy as np
import scipy.sparse as sps
import sys
import os
import csv
import math
import json
import requests
import boto3

sc = SparkContext()


if os.environ["APP_SETTINGS"] == "config.DevelopmentConfig":
    small_ratings = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest-small/ratings.csv')
    large_ratings = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest/ratings.csv')
    small_movies = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest-small/movies.csv')
    large_movies = os.path.join('file:/Users/camlinke/Dropbox/780/projects/movie-recommender/ml_data/ml-latest/ratings.csv')
else:
    small_ratings = os.path.join('../ratings.csv')
    # AWS_ACCESS_ID = os.environ['AWS_ACCESS_ID']
    # AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
    # session = boto3.Session(aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)
    # s3 = session.resource('s3')
    # small_ratings = s3.Object('movie-recommender', 'ml_data/ml-latest-small/ratings.csv').get('ratings.csv')
    # # key = s3.get_bucket('media.yourdomain.com').get_key('examples/first_file.csv')
    # # key.get_contents_to_filename('/myfile.csv')


num_partitions = 2
user_id = None

if len(sys.argv) > 0:
    for arg in sys.argv:
        if arg == "large":
            raw_ratings = sc.textFile(large_ratings).repartition(num_partitions)
            # raw_movies = sc.textFile(large_movies)
        if arg == "small":
            raw_ratings = sc.textFile(small_ratings).repartition(num_partitions)
            # raw_movies = sc.textFile(small_movies)
        if arg[:3] == "id:":
            user_id = arg[3:]
else:
    raw_ratings = sc.textFile(small_ratings).repartition(num_partitions)
    # raw_movies = sc.textFile(small_movies)

fake_user_ratings = [(1, 5), (7, 3), (173, 2), (99, 1), (88, 5), (288, 5), (405, 3), (296, 5), (47, 5), (1432, 4)]
user_seen_movies_list = [x[0] for x in fake_user_ratings]

def get_ratings_tuple(entry):
    items = entry.split(',')
    return int(items[0]), int(items[1]), float(items[2])

header = raw_ratings.first()
ratingsRDD = raw_ratings.filter(lambda line: line != header).map(get_ratings_tuple).cache()

# Cosine Similarity for Individual Recommendations
def cosine_similarity(user1, user2):
    """ Takes in two Dense Vectors of user's Recommendations and
        returns the cosine similarity between the two.
    """
    return user1.dot(user2) / (math.sqrt(user1.dot(user1)) * math.sqrt(user2.dot(user2)))


def similarities_for_user(user_id, crossRDD):
    """
    Takes in a user_id and and RDD of crossed user_ids with that user
    Returns an array of the top users who are most similar to a user.
    Note - the consine similarity is subtracted from 1 to give us the top rated
    users. With Cosine similarity the smaller the value the closer A and B are,
    in this case we later rank the higher the simliarity score the closer it is
    to the user, and we multiply that by their movie ratings to give us how much 
    they could "like" the movie.
    """
    similarities = (crossRDD
                    .filter(lambda x: x[0][0] == user_id)
                    .map(lambda x: (x[0][0], x[1][0], 1 - cosine_similarity(x[0][1], x[1][1]))))
    return (similarities
            .filter(lambda x: x[0] == int(user_id)))

def similarities_for_vector(user_id, user_data_rdd, user_ids_with_ratings_rdd):
    """
    Takes in a tuple of form (user_id, sparse_vector_of_ratings) and combines it with existing
    rating rdd. Returns cosine similarities for that user with existing users
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
    return mostSimilarForUserRDD.map(lambda x: (x[1], x[2]))
    # return mostSimilarForUserRDD.sortBy(lambda x: -x[2]).map(lambda x: (x[1], x[2]))

def get_top_movies_for_user(user_ratings=fake_user_ratings, ratings_rdd=ratingsRDD):
    movies_length = ratings_rdd.map(lambda x: x[1]).max() + 1
    user_ids_with_ratings_rdd = (ratings_rdd
                                 .map(lambda (user_id, movie_id, rating): (user_id, [(movie_id, rating)]))
                                 .reduceByKey(lambda a, b: a + b)
                                 .filter(lambda x: len(x[1]) > 25)
                                 .map(lambda x: (x[0], Vectors.sparse(movies_length, x[1]))))
    user_seen_movies_list = [x[0] for x in user_ratings]
    most_similar_for_user_rdd = create_most_similar_for_user_rdd(user_ratings, user_ids_with_ratings_rdd, movies_length)
    similar_users_and_similarity_rdd = create_similar_users_and_similarity_rdd(most_similar_for_user_rdd)
    top_movies_for_user = (user_ids_with_ratings_rdd
                           .join(similar_users_and_similarity_rdd)
                           .flatMap(lambda x: create_id_rating_tuples(x[1][1], x[1][0]))
                           .filter(lambda x: x[0] not in user_seen_movies_list)
                           .reduceByKey(lambda a, b: max(a, b))
                           .takeOrdered(100, lambda x: -x[1]))
    return top_movies_for_user


if os.environ["APP_SETTINGS"] == "config.ProductionConfig":
    ratings = requests.get('http://ec2-52-88-144-76.us-west-2.compute.amazonaws.com/api/users/{}'.format(user_id)).json()['ratings']
    user_ratings = [(int(id), int(rating)) for id, rating in ratings if rating != 0]
    recommendations = {key: value for key, value in get_top_movies_for_user(user_ratings=user_ratings)}
    r = requests.post('http://ec2-52-88-144-76.us-west-2.compute.amazonaws.com/api/users/{}'.format(user_id), data=json.dumps({"recommendations" : recommendations}))
    print r.text
else:
    ratings = requests.get('http://localhost:5000/api/users/{}'.format(user_id)).json()['ratings']
    user_ratings = [(int(id), int(rating)) for id, rating in ratings if rating != 0]
    recommendations = {key: value for key, value in get_top_movies_for_user(user_ratings=user_ratings)}
    r = requests.post('http://localhost:5000/api/users/{}'.format(user_id), data=json.dumps({"recommendations" : recommendations}))
    print r.text





# Collaborative Filtering, might do something with this later so I didn't want to delete it
# Most of this is from the Spark Course I took

# def get_movie_tuple(entry):
#     items = entry.split(',')
#     return int(items[0]), items[1]

# def get_counts_and_averages(IDandRatingsTuple):
#     id = IDandRatingsTuple[0]
#     length = len(IDandRatingsTuple[1])
#     average = 1.0 * sum(IDandRatingsTuple[1]) / length
#     return (id, (length, average))

# def compute_error(predictedRDD, actualRDD):
#     # Transform predictedRDD into the tuples of the form ((UserID, MovieID), Rating)
#     predictedReformattedRDD = predictedRDD.map(lambda x: ((x[0], x[1]), x[2]))

#     # Transform actualRDD into the tuples of the form ((UserID, MovieID), Rating)
#     actualReformattedRDD = actualRDD.map(lambda x: ((x[0], x[1]), x[2]))

#     # Compute the squared error for each matching entry
#     squaredErrorsRDD = (predictedReformattedRDD
#                         .join(actualReformattedRDD)
#                         .map(lambda x: (x[0], (math.pow((x[1][0]-x[1][1]), 2)))))

#     totalError = sum(squaredErrorsRDD.values().take(squaredErrorsRDD.count()))

#     # Count the number of entries for which you computed the total squared error
#     numRatings = squaredErrorsRDD.count()

#     # Compute the RSME
#     return math.sqrt(totalError / numRatings)

# header = raw_movies.first()
# moviesRDD = raw_movies.filter(lambda line: line != header).map(get_movie_tuple).cache()
# movieIDsWithRatingsRDD = (ratingsRDD
#                           .map(lambda x: (x[1], x[2]))
#                           .groupByKey())
# movieIDsWithAvgRatingsRDD = movieIDsWithRatingsRDD.map(get_counts_and_averages)
# movieNameWithAvgRatingsRDD = (moviesRDD
#                               .join(movieIDsWithAvgRatingsRDD)
#                               .map(lambda x: (x[1][1][1], x[1][0], x[1][1][0])))
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







