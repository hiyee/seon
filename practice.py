#all the imports
from __future__ import with_statement
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our littel application
app = Flask(__name__)
app.config.from_object(__name__)
# app.config.from_envvar('FLASKR_SETTINGS' silent=True)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardwon_request(exception):
    g.db.close()


@app.route('/', methods=['GET', 'POST'])
def show_entries():
    cur = g.db.execute('select title, text, id from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]

    result = {'entries': entries}

    #mode = 0:add, 1:edit
    mode = 0

    if request.method == 'POST':
        result['origin_title'] = request.form['origin_title']
        result['origin_text'] = request.form['origin_text']
        result['id'] = request.form['id']
        mode = 1
        flash('EDIT MODE')

    result['mode'] = mode

    return render_template('show_entries.html', result=result)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'): # session['logged_in']
        abort(401)
    g.db.execute('insert into entries (title, text) values(?, ?)', [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/edit', methods=['POST'])
def edit_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('update entries set title = ?, text = ? where id = ?', [request.form['title'], request.form['text'], request.form['id']])
    g.db.commit()
    flash('successfully edit no.'+request.form['id'])
    return redirect(url_for('show_entries'))


@app.route('/del', methods=['POST'])
def del_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from entries where id = ?', [request.form['id']])
    g.db.commit()
    flash('successfully delete no.'+request.form['id'])
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            # session.setattribute('logged_in', True)

            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)

    # session['logged_in'] = None
    # del(session['logged_in'])
    flash('you were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()

