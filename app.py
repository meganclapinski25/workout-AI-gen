import os
from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
import psycopg2
import openai
import bcrypt
import re 

load_dotenv()

client1 = openai.OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

app = Flask(__name__)

# PostgreSQL Connection URL from .env
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/workoutpage')
def workoutpage():
    return render_template('workoutex.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username) VALUES (%s)', (username,))
        conn.commit()
        cur.close()
        session['username'] = username
        return redirect(url_for('profile', username=username))

@app.route('/users/<user_id>')
def profile(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    cur.close()
    context = {
        'user': user_data
    }
    return render_template('users.html', **context)

@app.route('/chatgbt_workout', methods=['GET', 'POST'])
def workoutgen():
    height = request.form.get('height')
    weight = request.form.get('weight')
    program = request.form.get('program')
    calorie = request.form.get('calorie')
    sex = request.form.get('sex')
    freq = request.form.get('freq')
    username = session.get('username')
    
    # Update database with new information
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE users
        SET height = %s, weight = %s, program = %s, calorie = %s, freq = %s, sex = %s
        WHERE username = %s
    ''', (height, weight, program, calorie, freq, sex, username))
    conn.commit()
    cur.close()
    
    prompt = f"Using {height} {weight} {sex} and their calorie goal:{calorie} create a workout program for {program} {freq} day(s) a week. Separate each workout by day"
    response = client1.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=4000
    )
    
    generated_response = response.choices[0].text.strip() 
    workouts = re.split(r'(?=Day \d+:)', generated_response.strip())
    print(f"Generated Response: {generated_response}")
    print(f"Workouts: {workouts}")
    return render_template('users.html', username=username, height=height, weight=weight, program=program, calorie=calorie, sex=sex, freq=freq, prompt=prompt, generated_response=generated_response, workouts=workouts)

@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit(user_id):
    if request.method == 'POST':
        updated_data = {
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'program': request.form.get('program'),
            'calories': request.form.get('calorie'),
            'sex': request.form.get('sex'),
            'freq': request.form.get('freq'),
        }
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE users
            SET height = %s, weight = %s, program = %s, calorie = %s, freq = %s, sex = %s
            WHERE id = %s
        ''', (updated_data['height'], updated_data['weight'], updated_data['program'], updated_data['calories'], updated_data['freq'], updated_data['sex'], user_id))
        conn.commit()
        cur.close()
        return redirect(url_for('profile', user_id=user_id))
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user_data = cur.fetchone()
        cur.close()
        context = {
            'user': user_data
        }
        return render_template('edit.html', **context)

if __name__ == '__main__':
    app.run(debug=True)
