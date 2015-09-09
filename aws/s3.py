import boto3
import uuid
import os

AWS_ACCESS_ID = os.environ['AWS_ACCESS_ID']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']

class S3:
    def __init__(self):
        self.session = boto3.Session(aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)
        self.s3 = self.session.resource('s3')

    def upload_file(self):
        #small
        self.s3.Object('movie-recommender', 'ml_data/ml-latest-small/movies.csv').put(Body=open("{}/ml-latest/movies.csv".format(os.environ["MOVIE_DATA_LOCATION"]), "rb"))
        self.s3.Object('movie-recommender', 'ml_data/ml-latest-small/links.csv').put(Body=open("{}/ml-latest/links.csv".format(os.environ["MOVIE_DATA_LOCATION"]), "rb"))
        self.s3.Object('movie-recommender', 'ml_data/ml-latest-small/ratings.csv').put(Body=open("{}/ml-latest-small/ratings.csv".format(os.environ["MOVIE_DATA_LOCATION"]), "rb"))

        #all
        self.s3.Object('movie-recommender', 'ml_data/ml-latest/movies.csv').put(Body=open("{}/ml-latest/movies.csv".format(os.environ["MOVIE_DATA_LOCATION"]), "rb"))
        self.s3.Object('movie-recommender', 'ml_data/ml-latest/links.csv').put(Body=open("{}/ml-latest/links.csv".format(os.environ["MOVIE_DATA_LOCATION"]), "rb"))
        self.s3.Object('movie-recommender', 'ml_data/ml-latest/ratings.csv').put(Body=open("{}/ml-latest/ratings.csv".format(os.environ["MOVIE_DATA_LOCATION"]), "rb"))

        
s = S3()
s.upload_file()
print s