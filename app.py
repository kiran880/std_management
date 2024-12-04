from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from functools import wraps
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set secret key from environment variable or use a default one
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Rate limiter configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# PostgreSQL Database Configuration
DB_USER = "postgres"
DB_PASSWORD = quote_plus("Kiran2001")
DB_HOST = "st-dbs.cnaekug4ubwz.eu-north-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_PORT = "5432"

print("\nDatabase Configuration:")
print(f"Host: {DB_HOST}")
print(f"Port: {DB_PORT}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")

# Configure SQLAlchemy with AWS RDS
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

print(f"\nConnecting to database: {DATABASE_URL.replace(DB_PASSWORD, '****')}")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class School(db.Model):
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    students = db.relationship('Student', backref='school_info', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    attendance = db.Column(db.Float, nullable=False, default=0.0)
    grade = db.Column(db.String(2), nullable=False)
    class_name = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create all database tables
with app.app_context():
    try:
        print("\nDropping existing tables if any...")
        db.drop_all()
        print("Creating fresh database tables in AWS RDS...")
        db.create_all()
        print("Database tables created successfully in AWS RDS!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise e

# Rate limiting decorator
def rate_limit(limit=30, per=60):
    def decorator(f):
        last_reset = time.time()
        calls = 0
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            nonlocal last_reset, calls
            
            now = time.time()
            if now - last_reset > per:
                calls = 0
                last_reset = now
                
            calls += 1
            if calls > limit:
                time_to_wait = per - (now - last_reset)
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                calls = 1
                last_reset = time.time()
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
@limiter.limit("10 per minute")
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

# School routes
@app.route('/schools')
@limiter.limit("10 per minute")
def list_schools():
    schools = School.query.all()
    return render_template('schools/index.html', schools=schools)

@app.route('/schools/add', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def add_school():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']

        try:
            school = School(
                name=name,
                address=address,
                phone=phone
            )
            db.session.add(school)
            db.session.commit()
            flash('School added successfully!', 'success')
            return redirect(url_for('list_schools'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding school. Name might be duplicate.', 'error')
            return redirect(url_for('add_school'))

    return render_template('schools/add.html')

@app.route('/schools/edit/<int:id>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def edit_school(id):
    school = School.query.get_or_404(id)
    
    if request.method == 'POST':
        school.name = request.form['name']
        school.address = request.form['address']
        school.phone = request.form['phone']

        try:
            db.session.commit()
            flash('School updated successfully!', 'success')
            return redirect(url_for('list_schools'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating school.', 'error')
            return redirect(url_for('edit_school', id=id))

    return render_template('schools/edit.html', school=school)

@app.route('/schools/delete/<int:id>')
@limiter.limit("10 per minute")
def delete_school(id):
    school = School.query.get_or_404(id)
    if school.students:
        flash('Cannot delete school with existing students.', 'error')
        return redirect(url_for('list_schools'))
        
    try:
        db.session.delete(school)
        db.session.commit()
        flash('School deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting school.', 'error')
    return redirect(url_for('list_schools'))

# Student routes
@app.route('/add', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def add_student():
    schools = School.query.all()
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        address = request.form['address']
        school_id = request.form['school_id']
        attendance = request.form['attendance']
        grade = request.form['grade']
        class_name = request.form['class_name']

        try:
            student = Student(
                name=name,
                roll_no=roll_no,
                age=age,
                gender=gender,
                phone=phone,
                address=address,
                school_id=school_id,
                attendance=attendance,
                grade=grade,
                class_name=class_name
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding student. Roll number might be duplicate.', 'error')
            return redirect(url_for('add_student'))

    return render_template('add.html', schools=schools)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def edit_student(id):
    student = Student.query.get_or_404(id)
    schools = School.query.all()
    
    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.gender = request.form['gender']
        student.phone = request.form['phone']
        student.address = request.form['address']
        student.school_id = request.form['school_id']
        student.attendance = request.form['attendance']
        student.grade = request.form['grade']
        student.class_name = request.form['class_name']

        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student.', 'error')
            return redirect(url_for('edit_student', id=id))

    return render_template('edit.html', student=student, schools=schools)

@app.route('/delete/<int:id>')
@limiter.limit("10 per minute")
def delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting student.', 'error')
    return redirect(url_for('index'))

@app.route('/test-db')
def test_db():
    try:
        # Test database connection
        schools_count = School.query.count()
        students_count = Student.query.count()
        return f"Database connection successful! Current data: {schools_count} schools, {students_count} students"
    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
