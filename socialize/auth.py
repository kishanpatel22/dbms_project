import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from socialize.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        birthday = request.form['birthday']
        email = request.form['email']
        phone = request.form['phone']

        print(username, password, birthday, email, phone)
        print(type(username), type(password), type(birthday), type(email), type(phone))

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT user_id FROM user_info WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            # inserts into user_info table
                # INSERT INTO user_info (username, password, email_id)
            db.execute(
                """
                INSERT INTO user_info (username, password, data_of_birth, email_id, phone_number)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, password, birthday, email, phone)
                # (username, password, email)
                # (username, generate_password_hash(password))
            )
            user_id = db.execute(
                'SELECT user_id FROM user_info WHERE username = ?', (username,)
            ).fetchone()[0]
            # inserts into user table

            db.execute(
                """
                INSERT INTO user (user_id)
                VALUES (?)
                """,
                (user_id,)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user_info WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # elif not check_password_hash(user['password'], password):
        elif user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('socialize.user_feed'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user_info WHERE user_id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


