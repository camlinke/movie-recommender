from app import app
from flask import render_template

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/rate')
def rate():
    return render_template('rate.html')

@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')