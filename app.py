import os
from flask import Flask, request, render_template, redirect, url_for, session
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
import certifi
import openai
import bcrypt




# get this path from the panel on mongodb.com
#meganclapinski
#pjqBwnbY83tONHQ6




app = Flask(__name__)
load_dotenv()
ca = certifi.where()
# get this path from the panel on mongodb.com
uri = "mongodb+srv://meganclapinski:pjqBwnbY83tONHQ6@firstdata.2divsl3.mongodb.net/test?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=ca)
# Get the database named plantsdatabase
temp = client.usersdatabase

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)




openai.api_key = os.environ.get('API_KEY')




API_KEY = os.getenv('API_KEY')
API_URL = 'https://api.openai.com/v1/chat/completions'

@app.route('/')
def homepage():
    if 'username' in session:
        return 'You are logged in as ' + session['username']
    return render_template('index.html')

@app.route('/workoutpage')
def workoutpage():
    return render_template('workoutex.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        returning_user = temp.db.users.find_one({'username': username})
        if returning_user:
            return render_template('index.html')
        
        user_data = {'username': username, 'password': password}
        temp.db.users.insert_one(user_data)
        
        
        return redirect(url_for('homepage'))
    
    


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