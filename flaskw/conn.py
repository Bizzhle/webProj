import sqlite3
import click
# g is used to store data that might be accessed by multiple functions during a request,
from flask import current_app, g
from flask.cli import with_appcontext


def get_conn():
    if 'conn' not in g:
        g.conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.conn.row_factory = sqlite3.Row

    return g.conn


def close_conn(e=None):
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()


def init_conn():
    conn = get_conn()

    with current_app.open_resource('schema.sql') as f:
        conn.executescript(f.read().decode('utf8'))


@click.command('init-conn')
@with_appcontext
def init_conn_command():
    """Clear the existing data and create new tables."""
    init_conn()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_conn)
    app.cli.add_command(init_conn_command)
