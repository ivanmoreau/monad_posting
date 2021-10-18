from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

#from monad_posting.auth import login_required
from monad_posting.db import get_db
from monad_posting.auth import login_required

bp = Blueprint("interface", __name__)

@bp.route("/", methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        post = request.form['posting']
        db = get_db()
        error = None

        if not post:
            error = 'Post is required.'

        if len(post) >= 400:
            error = 'Invalid: post too long.'

        if error is None:
            db.execute(
                'INSERT INTO POST (user_id, post_text, post_is_repost, post_date) VALUES ({}, "{}", False, CURTIME())'.format(g.user['user_id'], post)
            )

            return redirect(url_for('interface.index'))

        flash(error)

    db = get_db()
    post = None
    if g.user:
        posts = db.execute(""" SELECT post_id, user_id, post_text,
        post_is_repost, post_father_id, post_date FROM POST 
        WHERE user_id NOT IN (SELECT user_id_source 
        from BLOCKED_USER where user_id_target ={})
        ORDER
        BY post_date DESC LIMIT 30""".format(g.user['user_id'])).fetchall()
    else:
        posts = db.execute(""" SELECT post_id, user_id, post_text,
        post_is_repost, post_father_id, post_date FROM POST 
        ORDER
        BY post_date DESC LIMIT 31""").fetchall()
    
    return render_template("index.html", posts=posts, next=2)


@bp.route("/<int:page>", methods=("GET", "POST"))
def next(page):
    if request.method == 'POST':
        post = request.form['posting']
        db = get_db()
        error = None

        if not post:
            error = 'Post is required.'

        if error is None:
            db.execute(
                'INSERT INTO POST (user_id, post_text, post_is_repost, post_date) VALUES ({}, "{}", False, CURTIME())'.format(g.user['user_id'], post)
            )

            return redirect(url_for('interface.index'))

        flash(error)

    db = get_db()
    post = None
    if g.user:
        posts = db.execute(""" SELECT post_id, user_id, post_text,
        post_is_repost, post_father_id, post_date FROM POST 
        WHERE user_id NOT IN (SELECT user_id_source 
        from BLOCKED_USER where user_id_target ={})
        ORDER
        BY post_date DESC LIMIT {},{}""".format(g.user['user_id'],30*(page - 1), 30 + 1)).fetchall()
    else:
        posts = db.execute(""" SELECT post_id, user_id, post_text,
        post_is_repost, post_father_id, post_date FROM POST 
        ORDER
        BY post_date DESC LIMIT {},{}""".format(30*(page - 1), 30 + 1)).fetchall()
    return render_template("index.html", posts=posts, next=page+1)


@bp.route("/repost/<int:post_id>", methods=('GET', 'POST'))
@login_required
def repost(post_id):
    if request.method == 'POST':
        post = request.form['posting']
        db = get_db()
        error = None

        if not post:
            error = 'Post is required.'

        if len(post) >= 400:
            error = 'Invalid: post too long.'

        if error is None:
            db.execute(
                'INSERT INTO POST (user_id, post_text, post_is_repost, post_father_id, post_date) VALUES ({}, "{}", True, {}, CURTIME())'.format(g.user['user_id'], post, post_id)
            )

            return redirect(url_for('interface.index'))

        flash(error)

    db = get_db()
    post = db.execute(""" SELECT post_id, user_id, post_text,
    post_is_repost, post_father_id, post_date FROM POST 
    where post_id ={}""".format(post_id)).fetchone()
    return render_template("repost.html", post=post, next=2)


@bp.route("/settings")
@login_required
def settings():
    db = get_db()
    user = db.execute(""" SELECT USER_LOGIN.user_id, user_username, user_allowed,
    custom_css,
    user_name, user_description, user_mail FROM USER INNER JOIN USER_LOGIN ON 
    USER.user_id = USER_LOGIN.user_id INNER JOIN USER_PAGE ON USER_PAGE.user_id WHERE
    USER_LOGIN.user_id = {}""".format(g.user['user_id'])).fetchone()
    return render_template("settings.html", user=user, next=2)

@bp.route("/settings/upname", methods = ['GET', 'POST'])
@login_required
def upname():
    if request.method == 'POST':
        name = request.form['name']
        db = get_db()
        error = None

        if not name:
            error = 'Name is required.'

        if len(name) >= 255:
            error = 'Name too long.'

        if error is None:
            db.execute(
                'UPDATE USER SET user_name = "{}" WHERE user_id = {}'.format(name, g.user['user_id'])
            )

            return redirect(url_for('interface.settings'))

        flash(error)
    return redirect(url_for('interface.settings'))

@bp.route("/settings/updes", methods = ['GET', 'POST'])
@login_required
def updes():
    if request.method == 'POST':
        description = request.form['description']
        db = get_db()
        error = None

        if not description:
            error = 'Description is required.'

        if len(description) >= 450:
            error = 'Description too long.'

        if error is None:
            db.execute(
                'UPDATE USER SET user_description = "{}" WHERE user_id = {}'.format(description, g.user['user_id'])
            )

            return redirect(url_for('interface.settings'))

        flash(error)
    return redirect(url_for('interface.settings'))

@bp.route("/settings/uppass", methods = ['GET', 'POST'])
@login_required
def uppass():
    if request.method == 'POST':
        oldpass = request.form['oldpass']
        newpass = request.form['newpass']
        db = get_db()
        error = None

        if not oldpass:
            error = 'Old password is required.'

        if not newpass:
            error = 'New password is required.'

        if len(newpass) >= 20:
            error = 'Password too long.'

        user = db.execute(
            'SELECT * FROM USER_LOGIN WHERE user_id = {}'.format(g.user['user_id'])
        ).fetchone()

        if not check_password_hash(user['password_hash'], oldpass):
            error = 'Incorrect old password.'

        if error is None:
            db.execute(
                'UPDATE USER_LOGIN SET password_hash = "{}" WHERE user_id = {}'.format(generate_password_hash(newpass), g.user['user_id'])
            )
            return redirect(url_for('interface.settings'))
        flash(error)
    return redirect(url_for('interface.settings'))

@bp.route("/settings/upcss", methods = ['GET', 'POST'])
@login_required
def upcss():
    if request.method == 'POST':
        css = request.form['css']
        db = get_db()
        error = None

        if not css:
            error = 'css is required.'

        if len(css) >= 1024:
            error = 'css too long.'

        if error is None:
            db.execute(
                'UPDATE USER_PAGE SET custom_css = "{}" WHERE user_id = {}'.format(css, g.user['user_id'])
            )
            return redirect(url_for('interface.settings'))
        flash(error)
    return redirect(url_for('interface.settings'))


@bp.route("/p/<string:page>")
def profile(page):
    db = get_db()
    user = db.execute(""" SELECT user_username, user_name, user_description, USER.user_id, custom_css
    FROM USER INNER JOIN USER_PAGE ON USER_PAGE.user_id = USER.user_id where user_username = "{}" """.format(page)).fetchone()
    followers = db.execute(""" SELECT COUNT(*)
    FROM FOLLOWER where user_id_target = {} """.format(user['user_id'])).fetchone()
    following = db.execute(""" SELECT COUNT(*)
    FROM FOLLOWER where user_id_source = {} """.format(user['user_id'])).fetchone()
    posts = db.execute(""" SELECT post_id, user_id, post_text,
    post_is_repost, post_father_id, post_date FROM POST 
    where user_id = {}
    ORDER
    BY post_date DESC""".format(user['user_id'])).fetchall()
    follows = None
    blocks = None
    if g.user is not None:
        follows = db.execute(""" SELECT COUNT(*)
        FROM FOLLOWER where user_id_source = {} 
        AND user_id_target = {} """.format(g.user['user_id'], user['user_id'])).fetchone()[0]
        blocks = db.execute(""" SELECT COUNT(*)
        FROM BLOCKED_USER where user_id_source = {} 
        AND user_id_target = {} """.format(g.user['user_id'], user['user_id'])).fetchone()[0]
    return render_template("profile.html", user=user,
    followers=followers[0], following=following[0], posts=posts, follows=follows, blocks=blocks)


@bp.route("/p/<string:page>/follow")
@login_required
def follow(page):
    error = None
    if page == g.user['user_username']:
        error = 'Illegal exception: user is user.'
    if error is None:
        db = get_db()
        user = db.execute(""" SELECT user_username, user_name, user_description, user_id
        FROM USER where user_username = "{}" """.format(page)).fetchone()

        follows = db.execute(""" SELECT COUNT(*)
        FROM FOLLOWER where user_id_source = {} 
        AND user_id_target = {} """.format(g.user['user_id'], user['user_id'])).fetchone()[0]

        if follows == 0:
            db.execute(""" INSERT INTO FOLLOWER (user_id_source, user_id_target) VALUES ({},{}) """
            .format(g.user['user_id'], user['user_id']))
        else:
            db.execute(""" DELETE FROM FOLLOWER WHERE user_id_source = "{}" AND user_id_target = "{}" """
            .format(g.user['user_id'], user['user_id']))
        return redirect(url_for('interface.profile', page=page))
    flash(error)
    return redirect(url_for('interface.profile', page=page))

@bp.route("/p/<string:page>/block")
@login_required
def block(page):
    error = None
    if page == g.user['user_username']:
        error = 'Illegal exception: user is user.'
    if error is None:
        db = get_db()
        user = db.execute(""" SELECT user_username, user_name, user_description, user_id
        FROM USER where user_username = "{}" """.format(page)).fetchone()

        blocks = db.execute(""" SELECT COUNT(*)
        FROM BLOCKED_USER where user_id_source = {} 
        AND user_id_target = {} """.format(g.user['user_id'], user['user_id'])).fetchone()[0]

        if blocks == 0:
            db.execute(""" INSERT INTO BLOCKED_USER (user_id_source, user_id_target) VALUES ({},{}) """
            .format(g.user['user_id'], user['user_id']))
        else:
            db.execute(""" DELETE FROM BLOCKED_USER WHERE user_id_source = "{}" AND user_id_target = "{}" """
            .format(g.user['user_id'], user['user_id']))
        return redirect(url_for('interface.profile', page=page))

    flash(error)
    return redirect(url_for('interface.profile', page=page))


@bp.route("/delete/<int:post>")
@login_required
def delete(post):
    db = get_db()
    user = db.execute(""" SELECT user_id
        FROM POST where post_id = {} """.format(post)).fetchone()
    error = None
    if user['user_id'] != g.user['user_id']:
        error = 'Illegal exception: user invalid'
    posts_count = db.execute(""" SELECT *
        FROM POST where post_father_id = {} """.format(post)).fetchone()
    if posts_count is not None:
        error = 'Cannot delete posts with replies.'
    if error is None:
        db.execute(""" DELETE FROM POST WHERE post_id = {} """
            .format(post))
        return redirect(url_for('interface.profile', page=g.user['user_username']))

    flash(error)
    return redirect(url_for('interface.profile', page=g.user['user_username']))