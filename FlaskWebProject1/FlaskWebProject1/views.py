"""
Routes and views for the flask application.
"""
import datetime
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime
from flask import render_template
#from FlaskWebProject1 import app
from FlaskWebProject1.db import get_db
from FlaskWebProject1.db import init_db
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

bp = Blueprint('auth', __name__)

def connect_to():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)  
    return service

#@bp.route('/')
#@bp.route('/home')
def home():
    """Renders the home page."""
    #init_db()
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@bp.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@bp.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    #if request.method == 'POST':
    #    username = request.form['username']
    #    password = request.form['password']
    #    db = get_db()
    #    error = None
    #    user = db.execute(
    #        'SELECT * FROM user WHERE username = ?', (username,)
    #    ).fetchone()

    #    if user is None:
    #        error = 'Incorrect username.'
    #    elif not check_password_hash(user['password'], password):
    #        error = 'Incorrect password.'

    #    if error is None:
    #        session.clear()
    #        session['user_id'] = user['id']
    #        return redirect(url_for('index'))

    #    flash(error)

    #return render_template('login.html')
    service = connect_to()
    if service:
      session['user']=True   
    return render_template('login.html')

#@bp.before_app_request
#def load_logged_in_user():
    #user_id = session.get('user_id')

    #if user_id is None:
    #    g.user = None
    #else:
    #    g.user = get_db().execute(
    #        'SELECT * FROM user WHERE id = ?', (user_id,)
    #    ).fetchone()

    #global ser
    #if ser :
    #    g.user = True
    #else:
    #    g.user = None

@bp.route('/logout')
def logout():
    #session.clear()
    #global ser
    #ser = False
    session['user']=False
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

