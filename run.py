from app import app
# from pyspark import SparkContext, SparkConf
import os
app.config.from_object(os.environ['APP_SETTINGS']) # Pulls config from environment variable

if __name__ == '__main__':
    # conf = SparkConf().setAppName("movie_recommender")
    # sc = SparkContext(conf=conf, pyFiles=['engine.py'])
    # app = create_app(sc)
    app.run()