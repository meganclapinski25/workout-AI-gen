import os
from flask import Flask, request, render_template, redirect, url_for, session
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import certifi
import openai
from openai import OpenAI
import bcrypt
import re 

load_dotenv()




client1 = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

# get this path from the panel on mongodb.com
#meganclapinski
#Ohd3cAP1Xv1qa6Vn




app = Flask(__name__)



# get this path from the panel on mongodb.com
mongo_uri = os.environ.get('MONGODB_URI')

# Create a new client and connect to the server
client = MongoClient(mongo_uri)
# Get the database named plantsdatabase
temp = client.get_database('users')

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)

@app.route('/')
def homepage():

    return render_template('index.html')

@app.route('/workoutpage')
def workoutpage():
    return render_template('workoutex.html')








@app.route('/register', methods=['GET', 'POST'])
def register():
    #Used this in order to populate a new collection in database with the username 
    #before the user did anything to create a workout 
    if request.method == 'POST':
        username = request.form.get('username')

        user_data = {'username': username}
        temp.users.insert_one(user_data)
        session['username'] = username


        return redirect(url_for('profile', username=username))


@app.route('/users/<user_id>')
def profile(user_id):
    #Keeps username throuhg whole session. Will use this for edit and delete of profiles 

        user_data = temp.users.find_one({'_id': ObjectId(user_id)})  # Access users collection
        context = {
            'user': user_data
        }
        return render_template('users.html', **context)




@app.route('/chatgbt_workout', methods=['GET', 'POST'])
def workoutgen():
    #Take in the users inputs/information and takes it through the prompt, of the chatgbt api

    height = request.form.get('height')
    weight = request.form.get('weight')
    program = request.form.get('program')
    calorie = request.form.get('calorie')
    sex = request.form.get('sex')
    freq = request.form.get('freq')
    username = session.get('username')
    #populates the database with the new information
    temp.users.update_one(
        {'username': username},
        {'$set': {'height': height, 'weight': weight, 'program': program, 'calorie': calorie, 'freq': freq, 'sex':sex}}
    )
    



    client1 = OpenAI()
    prompt = f"Using {height} {weight} {sex} and their calorie goal:{calorie} create a workout program for {program} {freq} day(s) a week. Seperate each workout by day"
    response = client1.completions.create(
     model="gpt-3.5-turbo-instruct",
     prompt = prompt,
    max_tokens=4000)
    
    generated_response = response.choices[0].text.strip() 
    workouts = re.split(r'(?=Day \d+:)', generated_response.strip())
    return render_template('users.html', username=username, height=height, weight=weight, program=program, calorie=calorie, sex=sex, freq=freq, prompt=prompt, generated_response=generated_response, workouts=workouts)
@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit(user_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        # TODO: Make an `update_one` database call to update the plant with the
        # given id. Make sure to put the updated fields in the `$set` object.
        updated_data = {
           'height' : request.form.get('height'),
            'weight' : request.form.get('weight'),
            'program' : request.form.get('program'),
            'calories' : request.form.get('calorie'),
            'sex' : request.form.get('sex'),
            'freq' : request.form.get('freq'),
            # Add more fields as needed
        }
        temp.users.update_one(
            {'_id': ObjectId(user_id)},  
            {'$set': updated_data}
        )

        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # TODO: Make a `find_one` database call to get the plant object with the
        # passed-in _id.
        plant_to_show = temp.users.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)
    print("Generated Response:", generated_response)  # Check the raw response
    print("Workouts List:", workouts)  # See what workouts are extracted

@app.route('/test_connection')
def test_connection():
    try:
        # Try to find one user
        user = temp.users.find_one()
        
        if user:
            return f"Connected to users database. Found user: {user['username']}"
        else:
            return "Connected to users database, but no users found."
    except Exception as e:
        return f"Failed to connect to users database: {e}"


if __name__ == '__main__':
    app.run(debug=True) 