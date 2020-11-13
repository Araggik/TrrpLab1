import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from FlaskWebProject1.db import init_db
from FlaskWebProject1.views import login_required
from FlaskWebProject1.views import service
from FlaskWebProject1.db import get_db
from flask import jsonify
from json import dumps

bp = Blueprint('blog', __name__)

@bp.route('/')
@bp.route('/home')
def index():
    #init_db()
    events =""
    if g.user:
      now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
      events_result = service.events().list(calendarId='primary', timeMin=now,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
      events = events_result.get('items', [])
    return render_template('blog.html', posts=events)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, complete)'
                ' VALUES (?, ?, ?, FALSE)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username,complete'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/change_complete', methods=('GET','POST'))
@login_required
def change_complete():
    id = request.form["id"]
    post = get_post(id)
    db = get_db()
    complete = not post['complete']
    db.execute('UPDATE post SET complete =? WHERE id = ?', (complete,id))
    db.commit()
    return complete


@bp.route('/delete_task', methods=('POST',))
@login_required
def delete_task():
    id = request.form["id"]
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return id