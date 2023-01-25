from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from tareasapp.auth import login_required
from tareasapp.db import get_db

bp = Blueprint('tareas', __name__)


@bp.route('/')
@login_required
def index():
    db, c = get_db()
    c.execute(
        #'SELECT * FROM task WHERE created_by = %s ORDER BY created_at DESC', (g.user,)
        'SELECT t.id, t.description, u.username, t.completed, t.created_at FROM task t JOIN user u ON t.created_by = u.id WHERE t.created_by = %s ORDER BY created_at DESC;', (g.user['id'],)
    )
    tareas = c.fetchall()

    return render_template('tareas/index.html', tareas=tareas)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        description = request.form['description']
        error = None
        
        if not description:
            error = 'Descripción es requerida.'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'INSERT INTO task (description, completed, created_by) VALUES (%s, %s, %s);',
                (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('tareas.index'))

    return render_template('tareas/create.html')


def get_tarea(id):
    db, c = get_db()
    c.execute(
        'SELECT t.id, t.description, t.completed, t.created_by, t.created_at, u.username'
        ' FROM task t JOIN user u ON t.created_by = u.id WHERE t.id = %s;',
        (id,)
    )
    tarea = c.fetchone()

    if tarea is None:
        abort(404, f"La tarea con id {id} no existe.")

    return tarea


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    tarea = get_tarea(id)

    if request.method == 'POST':
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not description:
            error = 'Descripción es requerida.'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'UPDATE task SET description = %s, completed = %s WHERE id = %s and created_by = %s;',
                (description, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('tareas.index'))

    return render_template('tareas/update.html', tarea=tarea)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    db, c = get_db()
    c.execute('DELETE FROM task WHERE id = %s and created_by = %s;', (id, g.user['id']))
    db.commit()
    return redirect(url_for('tareas.index'))