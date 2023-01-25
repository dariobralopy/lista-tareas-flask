import functools
from flask import (
    Blueprint, flash, g, render_template, request, url_for, redirect, session
)
from werkzeug.security import check_password_hash, generate_password_hash
from tareasapp.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
            'SELECT id FROM user WHERE username = %s;', (username,)
        )
        if not username:
            error = 'Nombre de usuario es requerido.'
        if not password:
            error = 'Contraseña es requerida.'
        elif c.fetchone() is not None:
            error = f"El nombre de usuario '{username}' no es encuentra disponible."

        if error is None:
            c.execute(
                'INSERT INTO user (username, password) VALUES (%s, %s);',
                (username, generate_password_hash(password))
            )
            db.commit()

            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = c.fetchone()

        if user is None:
            error = 'Ingrese nombre de usuario o contraseña correctamente.'
        elif not check_password_hash(user['password'], password):
            error = 'Ingrese nombre de usuario o contraseña correctamente.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('tareas.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db, c = get_db()
        c.execute(
            'SELECT * FROM user WHERE id = %s;', (user_id,)
        )
        g.user = c.fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))