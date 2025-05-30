import os
from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
import psycopg2
import openai
import bcrypt
import re 

load_dotenv()

client1 = openai.OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  
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


@app.route('/response')
def response():
    return render_template('response.html')

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
     # Generate workout plan using ChatGPT
    prompt = f"""
            You are a strength and conditioning coach for atheltes. Based on the user profile below, generate a personalized workout plan split into {freq} days. Each day should include 4–6 exercises with sets and reps. Include warm-up and cool-down suggestions. Do not repeat exercises across days. Use bullet points and keep language brief and motivational.

            At the end, add a final motivational note starting with 'Note:' on a new line.

            User Profile:
            - Height: {height}
            - Weight: {weight}
            - Sex: {sex}
            - Calorie goal: {calorie}
            - Goal: {program}
            """
    response = client1.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=2000
        )

    generated_response = response.choices[0].text.strip()
    if "Note:" in generated_response:
        workout_text, note_text = generated_response.rsplit("Note:", 1)
        note_text = note_text.strip()
    else:
        workout_text = generated_response
        note_text = None
    
    workouts = [day.strip() for day in generated_response.split("Day")[1:] if day.strip()]
    workout_cards = []
    
    if note_text and workouts:
   
        last_day = workouts[-1]
        if "Note:" in last_day:
            last_day = last_day.split("Note:")[0].strip()
            workouts[-1] = last_day

    
    for i, day in enumerate(workouts):
    # Remove leading number prefix like '3:' or '4:'
        day = re.sub(r'^\d+:\s*', '', day)

        day_content = f'<h2><strong>Day {i + 1}:</strong></h2>' + day.replace('\n', '<br>')
        workout_cards.append(day_content)
   
    
    return render_template(
        'users.html',
        username=username,
        height=height,
        weight=weight,
        program=program,
        calorie=calorie,
        sex=sex,
        freq=freq,
        generated_response=generated_response,
        workouts=workouts, 
        workout_cards= workout_cards,
        note_text= note_text
    )

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
