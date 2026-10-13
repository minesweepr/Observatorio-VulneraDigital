from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/analise')
def analise():
    return render_template('analise.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')