import os
import requests
import openai

from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo




app = Flask(__name__)

openai.api_key = os.environ.get('API_KEY')

load_dotenv
API_KEY = os.getenv('API_KEY')
API_URL = 'https://api.openai.com/v1/chat/completions'

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/workoutpage')
def workoutpage():
    return render_template('workoutex.html')

@app.route('/information', methods=['POST'])
def process_information():
    height = request.form.get('height')
    weight = request.form.get('weight')
    program = request.form.get('program')
    ##frequency = request.form.get('frequency')
    calories = request.form.get('calorie')

    return redirect(url_for('workoutgen', height=height, weight=weight, program=program, calorie=calories))





@app.route('/chatgbt_workout', methods=['GET'])
def workoutgen():
    height = request.args.get('height')
    weight = request.args.get('weight')
    program = request.args.get('program')
    calorie = request.args.get('calorie')

    prompt = f"Using {height} {weight} and their calorie goal:{calorie} create a workout program for {program}"
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt = prompt,
        max_tokens=400,
        
    )
    generated_response = response['choices'][0]['text']

    return render_template('response.html', height=height, weight=weight, program=program, calorie=calorie, prompt=prompt, generated_response=generated_response)




if __name__ == '__main__':
    app.run(debug=True)