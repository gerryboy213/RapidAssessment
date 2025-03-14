from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import uuid
import mysql.connector
from datetime import datetime


app = Flask(__name__)
CORS(app)  # Allows cross-origin requests from your Android app

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'form_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Add this to fetch results as dictionaries

# Database Configuration (Update your MySQL credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/form_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




def get_questions():
    return Questions.query.filter_by(category='HOME').all()

def notify_admin_new_submission(user_id):
    new_notification = UserResponse(
        user_id=user_id,
        question_number=0,  # Use 0 to indicate "completed assessment"
        response="Completed the assessment",
        is_read=False  # Mark as unread so admin sees the notification
    )
    db.session.add(new_notification)
    db.session.commit()



# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    control_num = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_initial = db.Column(db.String(5), nullable=True)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.String, nullable=False)  # Calculated automatically
    contact = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    region = db.Column(db.String(30), nullable=False)
    province = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    barangay = db.Column(db.String(30), nullable=False)
    street = db.Column(db.String(50), nullable=False)

    location = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)

class UserResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.Integer, nullable=False)  # Link to the user
    question_number = db.Column(db.Integer, nullable=False)
    response = db.Column(db.String(10), nullable=False)  # 'Yes' or 'No'
    is_read = db.Column(db.Boolean, default=False)
    
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin/login')
def admin():
    return render_template('admin_login.html')

@app.route('/admin/signup')
def admin_signup_page():
    return render_template('admin_signup.html')

@app.route('/admin/signup', methods=['POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['new_username']
        password = request.form['new_password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_admin = Admin(username=username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        
        flash('Admin account created successfully!', 'success')
        return redirect(url_for('admin_login'))

# Admin Login
@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin_data = Admin.query.filter_by(username=username).first()

        if admin_data and check_password_hash(admin_data.password, password):

            session['admin'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
            return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('admin'))

    admin = Admin.query.filter_by(username=session['admin']).first()
    questions = Questions.query.all()
    users = User.query.all()

    return render_template('admin_dashboard.html', admin=admin, questions=questions, users=users)

@app.route('/admin/update_profile', methods=['POST'])
def update_admin_profile():
    if 'admin' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('admin'))

    admin = Admin.query.filter_by(username=session['admin']).first()
    new_username = request.form['new_username']
    new_password = request.form['new_password']

    if new_username:
        admin.username = new_username

    if new_password:
        admin.password = generate_password_hash(new_password, method='pbkdf2:sha256')

    db.session.commit()
    session['admin'] = new_username  # Update session
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_question', methods=['POST'])
def add_question():
    if 'admin' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('admin'))

    question_text = request.form['question_text']
    translation = request.form['translation']

    new_question = Questions(question_text=question_text, translation=translation)
    db.session.add(new_question)
    db.session.commit()

    flash('Question added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_question/<int:question_id>', methods=['POST'])
def edit_question(question_id):
    if 'admin' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('admin'))

    question = Questions.query.get_or_404(question_id)
    question.question_text = request.form['question_text']
    question.translation = request.form['translation']
    db.session.commit()

    flash('Question updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_question/<int:question_id>')
def delete_question(question_id):
    if 'admin' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('admin'))

    question = Questions.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()

    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin'))

# Route for Form Submission
@app.route('/assessment', methods=['GET', 'POST'])
def assessmentss():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            middle_initial = request.form['middle_initial']
            last_name = request.form['last_name']
            dob = request.form['dob']
            contact=request.form['contact']
            sex = request.form['sex']
            region = request.form['region']
            province_name = request.form['province']
            city = request.form['city']
            barangay = request.form['barangay']
            street = request.form['street']
            location = request.form['location']
            date = request.form['date']

            # Calculate age from date of birth
            birth_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            new_user = User(
                first_name=first_name,
                middle_initial=middle_initial,
                last_name=last_name,
                dob=dob,
                age=age,
                contact=contact,
                sex=sex,
                region=region,
                province=province_name,
                city=city,
                barangay=barangay,
                street=street,
                location=location,
                date=date
            )

            db.session.add(new_user)
            db.session.commit()
            print("✅ Data saved successfully!")  # Debugging line
            
            session['user_id'] = new_user.id

            return redirect(url_for('questions'))  # Redirect after saving

        except Exception as e:
            print(f"❌ Error inserting data: {e}")  # Debugging line

    return render_template("assessment.html")

@app.route('/assessment', methods=['POST'])
def assessment():
    try:
        print("Incoming request:", request.data)  # Debugging

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON or missing Content-Type header"}), 400
        
        birth_date = datetime.strptime(data['dob'], '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        new_user = User(
            first_name=data['first_name'],
            middle_initial=data.get('middle_initial', ''),
            last_name=data['last_name'],
            dob=data['dob'],
            age=age,
            contact=data.get('contact', ''),
            sex=data.get('sex', ''),
            region=data.get('region', ''),
            province=data.get('province', ''),
            city=data.get('city', ''),
            barangay=data.get('barangay', ''),
            street=data.get('street', ''),
            location=data.get('location', ''),
            date=data.get('date', '')
        )

        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        return jsonify({"message": "Data saved successfully!", "user_id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/assessment', methods=['GET'])
def assessment_info():
    return jsonify({"message": "Please submit the form via POST method."}), 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json  # Receive JSON data from the Android app

        # Extract data from the request
        first_name = data['first_name']
        middle_initial = data['middle_initial']
        last_name = data['last_name']
        dob = data['dob']
        age = data['age']
        contact = data['contact']
        sex = data['sex']
        region = data['region']
        province = data['province']
        city = data['city']
        barangay = data['barangay']
        street = data['street']
        location = data['location']
        date = data['date']
        
        # Create a connection to the MySQL database
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        # Insert data into the MySQL database
        sql = """
        INSERT INTO user (first_name, middle_initial, last_name, dob, age, contact, sex, region, province, city, barangay, street, location, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (first_name, middle_initial, last_name, dob, age, contact, sex, region, province, city, barangay, street, location, date)
        cursor.execute(sql, values)
        connection.commit()
        
        user_id = cursor.lastrowid  # Get the ID of the last inserted row

        cursor.close()
        connection.close()

        return jsonify({"message": "Data inserted successfully", "user_id": user_id}), 201

    except Exception as e:
        print(f"❌ Error inserting data: {e}")  # Log the error
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_questions', methods=['GET'])
def get_questions():
    try:
        result = db.session.execute(text("SELECT id, question_text FROM questions"))
        questions = [{"id": row[0], "question_text": row[1]} for row in result.fetchall()]
        return jsonify(questions)
    except Exception as e:
        return jsonify([{"id": q[0], "question_text": q[1]} for q in questions])
    
@app.route('/save_answer', methods=['POST'])
def save_answer():
    try:
        data = request.json  # Get JSON data from request

        # Extract expected fields
        user_id = data.get('user_id')
        question_number = data.get('question_number')
        response = data.get('response')

        # Validate input
        if not all([user_id, question_number, response]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Connect to MySQL
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cursor = connection.cursor()

        # Insert the answer into the database
        sql = """
        INSERT INTO user_response (user_id, question_number, response)
        VALUES (%s, %s, %s)
        """
        values = (user_id, question_number, response)
        cursor.execute(sql, values)
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Answer saved successfully"}), 201

    except Exception as e:
        print(f"❌ Error saving answer: {e}")  # Debugging in terminal
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/update_control_number', methods=['POST'])
def update_control_number():
    try:
        data = request.json  # Get JSON data
        user_id = data.get("user_id")
        

        if not user_id:
            return jsonify({"success": False, "error": "Missing user_id"}), 400

        # Generate control_num
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")  # YYYYMMDDHHMMSS
        random_num = random.randint(10, 99)  # Two-digit random number
        control_num = f"CN-{user_id}-{current_time}{random_num}"

        # Connect to MySQL
        connection = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"]
        )
        cursor = connection.cursor()

        # Update the user table with the control number
        sql = "UPDATE user SET control_num = %s WHERE id = %s"
        cursor.execute(sql, (control_num, user_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "control_num": control_num}), 200

    except Exception as e:
        print(f"❌ Error updating control number: {e}")  # Debugging
        return jsonify({"success": False, "error": str(e)}), 500
    
    
@app.route('/get_control_number', methods=['GET'])
def get_control_number():
    user_id = request.args.get("user_id")  # Get user_id from request

    if not user_id:
        return jsonify({"success": False, "error": "Missing user_id"}), 400

    try:
        connection = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"]
        )
        cursor = connection.cursor()

        # ✅ Retrieve control number for the given user
        cursor.execute("SELECT control_num FROM user WHERE id = %s", (user_id,))
        result = cursor.fetchone()
       
        cursor.close()
        connection.close()

        if result and result[0]:  # Ensure result is not None
            return jsonify({"success": True, "control_num": result[0]})
        else:
            return jsonify({"success": False, "error": "No control number found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

import random
import string
from datetime import datetime


@app.route('/questions', methods=['GET', 'POST'])
def questions():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('assessment'))

    # Reset the question number if the session is from a new user
    if 'last_user_id' not in session or session['last_user_id'] != user_id:
        session['current_question_number'] = 1
        session['responses'] = {}  # Clear previous responses
        session['last_user_id'] = user_id  # Store the current user ID

    current_question_number = session.get('current_question_number', 1)
    total_questions = db.session.query(Questions).count()

    if current_question_number > total_questions:
        session['current_question_number'] = 1
        current_question_number = 1

    question = db.session.query(Questions).filter_by(id=current_question_number).first()
    is_last_question = current_question_number == total_questions

    if request.method == 'POST':
        if 'back' in request.form:
            current_question_number = max(1, current_question_number - 1)
            session['current_question_number'] = current_question_number
            return redirect(url_for('questions'))

        response = request.form.get(f'q{current_question_number}')
        if response:
            responses = session.get('responses', {})
            responses[str(current_question_number)] = response
            session['responses'] = responses

            new_response = UserResponse(user_id=user_id, question_number=current_question_number, response=response)
            db.session.add(new_response)
            db.session.commit()

        if is_last_question:
            return redirect(url_for('summary'))  # Redirect to the summary page

        session['current_question_number'] += 1
        return redirect(url_for('questions'))

    return render_template('questionnaire.html', question=question, is_last_question=is_last_question)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('assessment'))

    responses = session.get('responses', {})

    # Fetch all questions and match them with responses
    questions = db.session.query(Questions).filter(Questions.id.in_(responses.keys())).all()
    questions_with_answers = {q.id: {"question": q.question_text, "answer": responses.get(str(q.id))} for q in questions}

    if request.method == 'POST':
        # Generate a unique control number
        control_number = f"CN-{user_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

        # Assign the control number to the user
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            user.control_num = control_number
            db.session.commit()

        notify_admin_new_submission(user_id)

        return redirect(url_for('evaluate'))  # Redirect to evaluation page

    return render_template('summary.html', questions_with_answers=questions_with_answers)


@app.route('/admin/questions', methods=['GET', 'POST'])
def manage_questions():
    if request.method == 'POST':
        question_id = request.form['question_id']
        new_text = request.form['question_text']
        new_translation = request.form['translation']

        question = Questions.query.get(question_id)
        if question:
            question.question_text = new_text
            question.translation = new_translation
            db.session.commit()


    questions_list = get_questions()
    return render_template('admin_questions.html', questions=questions_list)

app.route('/ph-json/address')
def serve_json(address):
    return send_from_directory('static/ph-json', address)

@app.route('/evaluate')
def evaluate():
    responses = session.get('responses', {})
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('assessment'))

    # Fetch the user's control number
    user = db.session.query(User).filter_by(id=user_id).first()
    control_number = user.control_num if user else "N/A"

    key_question_numbers = [1, 4, 10]
    yes_answers = [int(q) for q, answer in responses.items() if answer.lower() == "yes"]

    if any(q in yes_answers for q in key_question_numbers):  
        return render_template('evaluatee.html', control_number=control_number)
    elif yes_answers:  
        return render_template('evaluate1.html', control_number=control_number)
    else:
        return render_template('evaluate2.html', control_number=control_number)


    
@app.route('/evaluatee')
def evaluatee():
    return render_template('evaluatee.html')

@app.route('/evaluate1')
def evaluate1():
    return render_template('evaluate1.html')

@app.route('/evaluate2')
def evaluate2():
    return render_template('evaluate2.html')

# Thank You Page
@app.route('/thank-you')
def thank_you():

    return render_template('thankyou.html')

# Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host='0.0.0.0', port=5500, debug=True)

