import os
import shutil

def build():
    # Create build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')

    # Copy static files and templates
    shutil.copytree('templates', 'build/templates')
    
    # Copy Python files
    shutil.copy2('app.py', 'build/')
    
    # Copy requirements
    shutil.copy2('requirements.txt', 'build/')

if __name__ == '__main__':
    build()
