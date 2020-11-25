"""
Routes and views for the flask application.
"""
import json
import datetime
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime
from flask import render_template
from FlaskWebProject1.db import get_db
from FlaskWebProject1.db import init_db
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

bp = Blueprint('auth', __name__)

#def connect_to():
#    creds = None

#    if os.path.exists('token.pickle'):
#        with open('token.pickle', 'rb') as token:
#            creds = pickle.load(token)

#    if not creds or not creds.valid:
#        if creds and creds.expired and creds.refresh_token:
#            creds.refresh(Request())
#        else:
#            flow = InstalledAppFlow.from_client_secrets_file(
#                'credentials.json', SCOPES)
#            creds = flow.run_local_server(port=0)

#        with open('token.pickle', 'wb') as token:
#            pickle.dump(creds, token)
    
#    service = build('calendar', 'v3', credentials=creds)  
#    return service

def connect_to():
    creds = None

    #if os.path.exists('token.pickle'):
    #    with open('token.pickle', 'rb') as token:
    #        creds = pickle.load(token)
    if session.get('cred'):
        creds = pickle.loads(session.get('cred'))

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        #with open('token.pickle', 'wb') as token:
        #    pickle.dump(creds, token)
            session['cred'] = pickle.dumps(creds)

    
    service = build('calendar', 'v3', credentials=creds)  
    return service

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

@bp.route('/login', methods=('GET', 'POST'))
def login():
    service = connect_to()
    if service:
      session['user']=True   
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session['user']=False
    session['cred']=None
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

