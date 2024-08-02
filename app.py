from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database configuration
DATABASE_URL = 'postgresql://flask_user:password@localhost/flask_app'

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            sql.SQL("INSERT INTO users (email, password) VALUES (%s, %s)"),
            [form.email.data, form.password.data]
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            sql.SQL("SELECT * FROM users WHERE email = %s AND password = %s"),
            [form.email.data, form.password.data]
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            session['user'] = form.email.data
            flash('Login successful!')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/welcome')
def welcome():
    if 'user' in session:
        return f'Welcome, {session["user"]}!'
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
