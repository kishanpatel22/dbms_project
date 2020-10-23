import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

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
        'SELECT * from posts order by created desc limit 10'
    ).fetchall()
    return render_template('socialize/feed.html', posts=posts)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        caption = request.form['image_caption']
        if not caption:
            flash('Caption is required.')
        
        # check if POST object has a file
        elif 'file' not in request.files:
            flash('No file part')

        # accept only if file has a name
        elif request.files['file'].filename == '':
            flash('No selected file')
        
        else:
            db = get_db()

            user_id = g.user['user_id']
            num_post = db.execute(
                """
                SELECT num_posts
                FROM user
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()['num_posts']
            image_url = f"{user_id}_{num_post+1}"

            file = request.files['file']
            if file and allowed_file(file.filename):
                extension = file.filename.rsplit('.', 1)[1].lower()
                # sanitize the filename
                filename = secure_filename(image_url) + '.' + extension
                file.save(os.path.join(current_app.config['IMAGE_FOLDER'], filename))

            db.execute(
                """
                INSERT INTO posts (image_caption, image_url, post_user_id)
                VALUES (?, ?, ?)
                """,
                (caption, image_url, user_id)
            )
            db.execute(
                """
                UPDATE user
                SET num_posts = num_posts+1
                WHERE user_id = ?
                """,
                (user_id,)
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


# user news feed 
@bp.route('/profile')
@login_required
def profile():
    return render_template('socialize/profile.html')


# user news feed 
@bp.route('/feed')
@login_required
def user_feed():
    db = get_db()
    posts = db.execute(
        'SELECT * from posts where post_user_id in' 
        '(SELECT user_id_following from connections where user_id_follower in' 
        '(SELECT user_id from user_info where user_id = ?))',
        (g.user['user_id'], )
    ).fetchall()
    return render_template('socialize/feed.html', posts=posts)


# connections 
@bp.route('/connection')
@login_required
def connection():
    db = get_db()
    peoples = db.execute(
                    'SELECT * from user_info where user_id not in '
                    '(SELECT user_id_following from connections where user_id_follower in ' 
                    '(SELECT user_id from user_info where user_id = ?))',
                    (g.user['user_id'],)
              ).fetchall()
    return render_template('socialize/connection.html', users=peoples)


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
