from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from functools import wraps
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# PostgreSQL Database Configuration
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD'))
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Configure PostgreSQL connection with connection pooling
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'pool_timeout': 30
}
app.secret_key = os.getenv('SECRET_KEY')

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

# Create tables
with app.app_context():
    db.create_all()

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
@rate_limit(limit=30, per=60)  # Limit to 30 requests per minute
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

# School routes
@app.route('/schools')
@rate_limit(limit=30, per=60)
def list_schools():
    schools = School.query.all()
    return render_template('schools/index.html', schools=schools)

@app.route('/schools/add', methods=['GET', 'POST'])
@rate_limit(limit=30, per=60)
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
@rate_limit(limit=30, per=60)
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
@rate_limit(limit=30, per=60)
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
@rate_limit(limit=30, per=60)
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
@rate_limit(limit=30, per=60)
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
@rate_limit(limit=30, per=60)
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

if __name__ == '__main__':
    app.run(debug=True)
