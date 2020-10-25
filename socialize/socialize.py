import os
from shutil import copyfile

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
        'SELECT * FROM posts ORDER BY created DESC LIMIT 10'
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
                image_url = secure_filename(image_url) + '.' + extension
                file.save(os.path.join(current_app.config['IMAGE_FOLDER'], image_url))

            db.execute(
                """
                INSERT INTO posts (image_caption, image_url, post_user_id, post_id)
                VALUES (?, ?, ?, ?)
                """,
                (caption, image_url, user_id, num_post + 1)
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
        'SELECT * FROM posts WHERE post_id = ? AND post_user_id = ?',
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
        """
        SELECT allposts.*, user_like.created
        FROM (
            SELECT *
            FROM (
                SELECT *
                FROM posts
                WHERE post_user_id IN (
                    SELECT user_id_following
                    FROM connections
                    WHERE user_id_follower = ?
                )

                UNION

                SELECT *
                FROM posts
                WHERE post_user_id = ?
            )
            ORDER BY created DESC
        ) AS allposts
        LEFT JOIN likes AS user_like
        ON user_like.post_id = allposts.post_id
            AND user_like.post_user_id = allposts.post_user_id
            AND user_like.user_id = ?
        """,
        (g.user['user_id'], g.user['user_id'], g.user['user_id'])
    ).fetchall()

    return render_template('socialize/feed.html', posts=posts)


# connections
@bp.route('/connection', methods=('GET', 'POST'))
@login_required
def connection():
    db = get_db()
    if request.method == 'POST':
        connection_user_id = request.form['new_user_id']
        db.execute(
            """
            INSERT INTO connections (user_id_follower, user_id_following)
            VALUES (?, ?)
            """,
            (g.user['user_id'], connection_user_id)
        )
        db.commit()
        return redirect(url_for('socialize.connection'))
    else:
        peoples = db.execute(
                """
                SELECT *
                FROM user_info
                WHERE user_id NOT IN (
                    SELECT user_id_following
                    FROM connections
                    WHERE user_id_follower = ?
                    )
                    AND user_id != ?
                """,
                (g.user['user_id'], g.user['user_id'])
                ).fetchall()
        return render_template('socialize/connection.html', users=peoples)


# user connections
@bp.route('/user_connection')
@login_required
def user_connection():
    db = get_db()
    user_friends = db.execute(
            """
            SELECT *
            FROM user_info
            WHERE user_id IN (
                SELECT user_id_following
                FROM connections
                WHERE user_id_follower = ?
            )
            """,
            (g.user['user_id'], )).fetchall()
    return render_template('socialize/user_connection.html', user_friends=user_friends)


@bp.route('/like/<int:post_id>/<int:post_user_id>')
@login_required
def like(post_id, post_user_id):
    db = get_db()
    db.execute(
        """
        INSERT INTO likes (user_id, post_id, post_user_id)
        VALUES (?, ?, ?)
        """,
        (g.user['user_id'], post_id, post_user_id)
    )
    db.commit()
    return redirect(url_for('socialize.user_feed'))


@bp.route('/share/<image_url>/<caption>')
@login_required
def share(image_url, caption):
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
    share_image_url = f"{user_id}_{num_post+1}." + image_url.rsplit(".")[-1]

    # file.save(os.path.join(current_app.config['IMAGE_FOLDER'], image_url))
    src = f"{current_app.config['IMAGE_FOLDER']}/{image_url}"
    dst = f"{current_app.config['IMAGE_FOLDER']}/{share_image_url}"
    copyfile(src, dst)

    db.execute(
        """
        INSERT INTO posts (image_caption, image_url, post_user_id, post_id)
        VALUES (?, ?, ?, ?)
        """,
        (caption, share_image_url, user_id, num_post + 1)
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
    return redirect(url_for('socialize.user_feed'))



# comment
@bp.route('/comment/<int:post_id>/<int:post_user_id>',  methods=('GET', 'POST'))
@login_required
def comment(post_id, post_user_id):
    db = get_db()
    if request.method == 'POST':
        user_comments = db.execute(
                        """
                        SELECT *
                        FROM comments
                        WHERE post_id = ?
                            AND post_user_id = ?
                            AND user_id = ?
                        """,
                        (post_id, post_user_id, g.user['user_id'])).fetchall()
        num_user_comments = len(user_comments)

        comment_text = request.form['comment']
        db.execute(
            """
            INSERT INTO comments (comment_id, user_id, post_id, post_user_id, comment_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (num_user_comments + 1, g.user['user_id'], post_id, post_user_id, comment_text))
        db.commit()

    # get request to the comments
    comments = db.execute(
            """
            SELECT *
            FROM comments
            WHERE post_id = ?
                AND post_user_id = ?
            ORDER BY created DESC
            """,
            (post_id, post_user_id)).fetchall()

    return render_template('socialize/comment.html', comments=comments,
                            post_id=post_id, post_user_id=post_user_id)



@bp.route('/delete/<int:post_id>/<image_url>')
@login_required
def delete(post_id, image_url):
    print(image_url)
    db = get_db()
    db.execute('DELETE FROM posts WHERE post_id = ? AND post_user_id = ?',
               (post_id, g.user['user_id']))
    db.execute(
        """
        UPDATE user
        SET num_posts = num_posts-1
        WHERE user_id = ?
        """,
        (g.user['user_id'],)
    )
    db.commit()
    return redirect(url_for('socialize.user_feed'))

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
"""
