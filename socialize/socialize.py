from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from socialize.auth import login_required
from socialize.db import get_db

"""
    The blueprint record operations to execute when registered on an application
    socialize blueprint is the main route for the web application
"""
bp = Blueprint('socialize', __name__)

# root file route 
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT * from posts order by timestamp desc limit 10'
    ).fetchall()
    return render_template('socialize/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['image_caption']
        body = request.form['image_url']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO posts (image_caption, image_url, post_user_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['user_id'])
            )
            db.commit()
            return redirect(url_for('socialize.index'))

    return render_template('socialize/create.html')


def get_post(post_id, post_user_id, check_author=True):
    post = get_db().execute(
        'SELECT * form posts where post_id = ? and post_user_id = ?',
        (post_id, post_user_id)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['post_user_id'] != g.user['user_id']:
        abort(403)

    return post

"""
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
            return redirect(url_for('socialize.index'))

    return render_template('socialize/update.html', post=post)



@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('socialize.index'))
"""
