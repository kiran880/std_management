# Student Management System

A modern web application for managing student and school information, built with Flask and PostgreSQL.

## Features

- Student Management (Add, Edit, Delete)
- School Management (Add, Edit, Delete)
- Dark/Light Mode Theme
- Responsive Design
- PostgreSQL Database Integration
- Modern UI with Bootstrap 5.3.0

## Requirements

- Python 3.12
- PostgreSQL Database
- Python packages listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kiran880/studentmanagementsystem.git
cd studentmanagementsystem
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following configuration:
```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
SECRET_KEY=your_secret_key
```

5. Run the application:
```bash
python app.py
```

## Project Structure

```
student_management_system/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── README.md          # Project documentation
└── templates/         # HTML templates
    ├── base.html      # Base template with layout
    ├── index.html     # Student list page
    ├── add.html       # Add student form
    ├── edit.html      # Edit student form
    └── schools/       # School management templates
        ├── index.html # School list page
        ├── add.html   # Add school form
        └── edit.html  # Edit school form
```

## Features

### Student Management
- View all students
- Add new students
- Edit existing student information
- Delete students
- Track attendance and grades

### School Management
- View all schools
- Add new schools
- Edit school information
- Delete schools (if no students are enrolled)

### UI Features
- Dark/Light mode toggle
- Responsive design
- Modern Bootstrap components
- User-friendly forms
- Interactive data tables