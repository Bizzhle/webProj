from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskw.auth import login_required
from flaskw.conn import get_conn

bp = Blueprint('blog', __name__)

bp.route('/')


def index():
    conn = get_conn()
    posts = conn.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('/blog.index.html', posts=posts)


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
            conn = get_conn()
            conn.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            conn.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):  # to fetch the post to b updated or deleted
    post = get_conn().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesnt exist.".format(id))

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
            error = 'Title is required'
        if error is not None:
            flash(error)
        else:
            conn = get_conn()
            conn.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?'
                (title, body, id)
            )
            conn.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

    @bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
