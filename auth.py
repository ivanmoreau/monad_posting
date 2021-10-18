import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from monad_posting.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute('SELECT * FROM USER WHERE user_id = {}'.format(user_id)).fetchone()
        )


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not mail:
            error = 'Mail is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT user_id FROM USER WHERE user_username = "{}"'.format(username)
        ).fetchone() is not None:
            error = 'User with that username is already registered.'
        elif db.execute(
            'SELECT user_id FROM USER_LOGIN WHERE user_mail = "{}"'.format(mail)
        ).fetchone() is not None:
            error = 'User with that mail is already registered.'

        if len(password) >= 20:
            error = 'Password too long.'
        if len(username) >= 100:
            error = 'Username too long.'
        if len(mail) >= 400:
            error = 'Mail too long.'
        

        if error is None:
            db.execute(
                'INSERT INTO USER_LOGIN (user_mail, password_hash) VALUES ("{}", "{}")'.format(mail, generate_password_hash(password))
            )
            id_u = db.execute('select user_id from USER_LOGIN WHERE user_mail = "{}"'.format(mail)).first()[0]
            db.execute(
                'INSERT INTO USER (user_id, user_username, user_allowed, user_name, user_description) VALUES ({}, "{}", {}, "Anon", "Hi, welcome to my profile.")'.format(id_u, username, True)
            )
            db.execute(
                'INSERT INTO USER_PAGE (user_id, custom_css) VALUES ({}, "/* custom Css */")'.format(id_u)
            )
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM USER_LOGIN WHERE user_mail = "{}"'.format(mail)
        ).fetchone()

        if user is None:
            error = 'Incorrect mail.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('interface.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('interface.index'))