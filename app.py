
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text 
from werkzeug.security import generate_password_hash, check_password_hash

from flask_cors import CORS
from flask import current_app
import os, json
import uuid
import mysql.connector
from datetime import datetime
from sqlalchemy import func



app = Flask(__name__)
CORS(app)  # Allows cross-origin requests from your Android app

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'heeadsss_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Add this to fetch results as dictionaries

# Database Configuration (Update your MySQL credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/mayorga_form_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Folder to save uploaded signatures
# UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Allowed extensions (optional but recommended)
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    control_num = db.Column(db.String(255), nullable=False)
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
    
    visible_to_rhu = db.Column(db.Boolean, default=True)  # <-- ADD THIS LINE
    visible_to_brgy = db.Column(db.Boolean, default=True)  # <-- ADD THIS LINE
    visible_to_hospital = db.Column(db.Boolean, default=True)  # <-- ADD THIS LINE
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('first_name', 'last_name', 'dob', 'contact', name='unique_user_identity'),
    )
    
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
    region = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

class Services(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    services_saved = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(50), nullable=False, default='brgy')

    
    user_id = db.Column(db.Integer, nullable=False)  # Link to the user

class Recommendations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recommendation_text = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)
    recommendation_saved = db.Column(db.Boolean, default=False)  # ✅ Add this
    source = db.Column(db.String(50), nullable=False, default='brgy')


class Signature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


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
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

@app.route('/personal-information', methods=['GET', 'POST'])
def assessmentss():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            middle_initial = request.form['middle_initial']
            last_name = request.form['last_name']
            dob = request.form['dob']
            contact = request.form['contact']
            sex = request.form['sex']
            region = request.form['region']
            province_name = request.form['province']
            city = request.form['city']
            barangay = request.form['barangay']
            street = request.form['street']
            location = request.form['location']
            date = request.form['date']

            # Check if the user already exists (based on full name and dob)
            existing_user = User.query.filter(
                and_(
                    User.first_name.ilike(first_name),
                    User.last_name.ilike(last_name),
                    User.dob == dob,
                    User.contact == contact,
                    User.region.ilike(region),
                    User.province.ilike(province_name),
                    User.city.ilike(city),
                    User.barangay.ilike(barangay),
                    User.street.ilike(street),
                    User.location.ilike(location)
                )
            ).first()

            if existing_user:
                flash('A record with this information already exists. Please check your details or ask help from your health service provider.', 'warning')
                return redirect(url_for('assessmentss'))

            # Calculate age
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
            print("✅ Data saved successfully!")

            session['user_id'] = new_user.id
            return redirect(url_for('questions'))

        except IntegrityError:
            db.session.rollback()
            flash('This user already exists (duplicate submission).', 'warning')
            return redirect(url_for('assessmentss'))

        except Exception as e:
            print(f"❌ Error inserting data: {e}")
            flash('An unexpected error occurred while saving your data.', 'danger')

    return render_template("personal_information.html")


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
        cursor = connection.cursor(dictionary=True)

        # ✅ ADDED: Check for duplicate entry
        check_sql = """
        SELECT * FROM user
        WHERE first_name = %s AND middle_initial = %s AND last_name = %s AND dob = %s
        """
        cursor.execute(check_sql, (first_name, middle_initial, last_name, dob))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({"error": "The client is already existing"}), 409  # 409 Conflict

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
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "error": "Missing user_id"}), 400

        # Lock the user row for update to prevent race conditions
        user = db.session.query(User).filter_by(id=user_id).with_for_update().first()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Center mappings
        center_codes = {
            "Gandara AFHF/RHU": ("0860", "01"),
            "Pagsanghan AFHF/RHU": ("0860", "02"),
            "Matuguinao AFHF/RHU": ("0860", "03"),
            "Gandara District Hospital": ("0860", "04"),
            "BHS Union AFHF": ("0837", "05"),
            "Mayorga AFHF/RHU": ("0837", "06"),
            "MacArthur AFHF/RHU": ("0837", "07"),
            "Javier AFHF/RHU": ("0837", "08"),
            "Abuyog AFHF/RHU": ("0837", "09"),
            "Abuyog District Hospital": ("0837", "10")
        }

        center_source_map = {
            "Gandara AFHF/RHU": "rhu",
            "Pagsanghan AFHF/RHU": "rhu",
            "Matuguinao AFHF/RHU": "rhu",
            "Gandara District Hospital": "hospital",
            "BHS Union AFHF": "brgy",
            "Mayorga AFHF/RHU": "rhu",
            "MacArthur AFHF/RHU": "rhu",
            "Javier AFHF/RHU": "rhu",
            "Abuyog AFHF/RHU": "rhu",
            "Abuyog District Hospital": "hospital"
        }

        center_name = user.location
        center_info = center_codes.get(center_name)
        center_source = center_source_map.get(center_name)

        if not center_info or not center_source:
            return jsonify({"success": False, "error": f"No codes/source for center: {center_name}"}), 400

        province_code, city_code = center_info

        # Only generate if not already set
        if not user.control_num:
            prefix = f"{province_code}-{city_code}-"

            # Lock rows with same prefix and get max control number
            max_control_num = db.session.query(func.max(User.control_num)).filter(
                User.control_num.like(f"{prefix}%")
            ).scalar()

            if max_control_num:
                try:
                    last_number = int(max_control_num.split("-")[-1])
                except ValueError:
                    last_number = 0
            else:
                last_number = 0

            next_number = last_number + 1
            control_num_candidate = f"{prefix}{next_number:05d}"

            # Extra safety: make sure the generated number doesn't exist
            while db.session.query(User).filter_by(control_num=control_num_candidate).first():
                next_number += 1
                control_num_candidate = f"{prefix}{next_number:05d}"

            user.control_num = control_num_candidate

            # Set visibility flags
            user.visible_to_brgy = (center_source == "brgy")
            user.visible_to_rhu = (center_source == "rhu")
            user.visible_to_hospital = (center_source == "hospital")

            db.session.commit()
            print("✅ Generated Control Number:", user.control_num)
            notify_admin_new_submission(user_id)
        else:
            print("ℹ️ Control number already exists:", user.control_num)

        return jsonify({"success": True, "control_num": user.control_num}), 200

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Integrity error: possible duplication"}), 500
    except Exception as e:
        db.session.rollback()
        print("❌ Error updating control number:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/get_control_number', methods=['GET'])
def get_control_number():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "Missing user_id"}), 400

    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Define center-to-code mapping
        center_codes = {
            "Gandara AFHF/RHU": ("0860", "01"),
            "Pagsanghan AFHF/RHU": ("0860", "02"),
            "Matuguinao AFHF/RHU": ("0860", "03"),
            "Gandara District Hospital": ("0860", "04"),
            "BHS Union AFHF": ("0837", "05"),
            "Mayorga AFHF/RHU": ("0837", "06"),
            "MacArthur AFHF/RHU": ("0837", "07"),
            "Javier AFHF/RHU": ("0837", "08"),
            "Abuyog AFHF/RHU": ("0837", "09"),
            "Abuyog District Hospital": ("0837", "10")
        }

        center_name = user.location
        center_info = center_codes.get(center_name)

        if not center_info:
            return jsonify({"success": False, "error": f"No codes defined for center: {center_name}"}), 400

        province_code, city_code = center_info

        # Generate control number if not set
        if not user.control_num:
            prefix = f"{province_code}-{city_code}-"
            existing_controls = db.session.query(User.control_num).filter(
                User.control_num.like(f"{prefix}%")
            ).all()

            existing_numbers = sorted([
                int(control[0].split("-")[-1])
                for control in existing_controls if control[0]
            ])

            count_number = 1
            for num in existing_numbers:
                if num == count_number:
                    count_number += 1
                else:
                    break

            control_number = f"{prefix}{count_number:05d}"
            user.control_num = control_number
            db.session.commit()

            print("✅ Generated control number:", control_number)
        else:
            control_number = user.control_num

        return jsonify({"success": True, "control_num": control_number}), 200

    except Exception as e:
        print("❌ Error in get_control_number:", e)
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
    user = db.session.query(User).filter_by(id=user_id).first()

    questions = db.session.query(Questions).filter(Questions.id.in_(responses.keys())).all()
    questions_with_answers = {
        q.id: {"question": q.question_text, "answer": responses.get(str(q.id))} for q in questions
    }

    if request.method == 'POST':
        if not user:
            return "Error: User not found", 404

        # Define center-to-code and source mappings
        center_codes = {
            "Gandara AFHF/RHU": ("0860", "01"),
            "Pagsanghan AFHF/RHU": ("0860", "02"),
            "Matuguinao AFHF/RHU": ("0860", "03"),
            "Gandara District Hospital": ("0860", "04"),
            "BHS Union AFHF": ("0837", "05"),
            "Mayorga AFHF/RHU": ("0837", "06"),
            "MacArthur AFHF/RHU": ("0837", "07"),
            "Javier AFHF/RHU": ("0837", "08"),
            "Abuyog AFHF/RHU": ("0837", "09"),
            "Abuyog District Hospital": ("0837", "10")
        }

        center_source_map = {
            "Gandara AFHF/RHU": "rhu",
            "Pagsanghan AFHF/RHU": "rhu",
            "Matuguinao AFHF/RHU": "rhu",
            "Gandara District Hospital": "hospital",
            "BHS Union AFHF": "brgy",
            "Mayorga AFHF/RHU": "rhu",
            "MacArthur AFHF/RHU": "rhu",
            "Javier AFHF/RHU": "rhu",
            "Abuyog AFHF/RHU": "rhu",
            "Abuyog District Hospital": "hospital"
        }

        center_name = user.location
        center_info = center_codes.get(center_name)
        center_source = center_source_map.get(center_name)

        if not center_info or not center_source:
            return f"Error: No codes or source mapping defined for center: {center_name}", 400

        province_code, city_code = center_info

        # Generate control number if not set
        if not user.control_num:
            prefix = f"{province_code}-{city_code}-"

            from sqlalchemy import func
            max_control_num = db.session.query(func.max(User.control_num)).filter(
                User.control_num.like(f"{prefix}%")
            ).scalar()

            if max_control_num:
                last_number = int(max_control_num.split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1

            user.control_num = f"{prefix}{next_number:05d}"

        # Set visibility based on center type
        user.visible_to_rhu = (center_source == "rhu")
        user.visible_to_brgy = (center_source == "brgy")
        user.visible_to_hospital = (center_source == "hospital")

        db.session.commit()
        print("✅ Control number and visibility saved.")
        notify_admin_new_submission(user_id)

        return redirect(url_for('evaluate'))

    return render_template('summary.html', questions_with_answers=questions_with_answers, control_number=user.control_num)




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

@app.route('/get_results', methods=['GET'])
def get_results():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # Fetch "Yes" responses for the user
    responses = db.session.query(UserResponse).filter_by(user_id=user_id).all()
    yes_responses = [r for r in responses if r.response == "Yes"]

    if not yes_responses:
        return jsonify({"results": []})

    # Get the question numbers from those responses
    question_ids = [r.question_number for r in yes_responses]

    # Fetch corresponding question texts
    questions = db.session.query(Questions).filter(Questions.id.in_(question_ids)).all()
    question_map = {q.id: q.question_text for q in questions}

    # Build result
    result = [
        {
            "question": question_map.get(r.question_number, f"Question #{r.question_number}"),
            "answer": r.response
        }
        for r in yes_responses if r.question_number in question_map
    ]

    return jsonify({"results": result})


@app.route('/save_services_and_recommendations', methods=['POST'])
def save_services_and_recommendations():
    data = request.get_json()
    print("Received data:", data)

    user_id = data.get('user_id')
    services = data.get('services', [])
    recommendations = data.get('recommendations', [])

    if not user_id:
        return jsonify({"error": "user_id is missing"}), 400

    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Determine source based on user location
        center_source_map = {
            "Gandara AFHF/RHU": "rhu",
            "Pagsanghan AFHF/RHU": "rhu",
            "Matuguinao AFHF/RHU": "rhu",
            "Gandara District Hospital": "hospital",
            "BHS Union AFHF": "brgy",
            "Mayorga AFHF/RHU": "rhu",
            "MacArthur AFHF/RHU": "rhu",
            "Javier AFHF/RHU": "rhu",
            "Abuyog AFHF/RHU": "rhu",
            "Abuyog District Hospital": "hospital"
        }

        source = center_source_map.get(user.location, "brgy")  # Default to 'brgy'

        for key in center_source_map:
            if key in user.location:
                source = center_source_map[key]
                break

        # Save services
        for service in services:
            new_service = Services(
                service_name=service,
                user_id=user_id,
                services_saved=True,
                source=source
            )
            db.session.add(new_service)

        # Save recommendations
        for rec in recommendations:
            new_recommendation = Recommendations(
                recommendation_text=rec,
                user_id=user_id,
                recommendation_saved=True,
                source=source
            )
            db.session.add(new_recommendation)

        db.session.commit()
        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print("Error saving data:", e)
        return jsonify({"error": str(e)}), 500




    
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
