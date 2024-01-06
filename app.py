import os
import requests

from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo



app = Flask(__name__)

load_dotenv
API_KEY = os.getenv('API_KEY')
API_URL = 'https://api.openai.com/v1/chat/completions'

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/workoutpage')
def workoutpage():
    return render_template('workoutex.html')


if __name__ == '__main__':
    app.run(debug=True)