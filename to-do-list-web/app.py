from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla de tareas si no existe
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    status = 'Pendiente'
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (title, status, created_at) VALUES (?, ?, ?)', (title, status, created_at))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    new_status = request.form['status']
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/filter', methods=['GET'])
def filter_tasks():
    status = request.args.get('status')
    conn = get_db_connection()
    if status:
        tasks = conn.execute('SELECT * FROM tasks WHERE status = ?', (status,)).fetchall()
    else:
        tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/statistics')
def statistics():
    conn = get_db_connection()
    total_tasks = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    pending_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', ('Pendiente',)).fetchone()[0]
    in_progress_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', ('En Proceso',)).fetchone()[0]
    completed_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', ('Finalizada',)).fetchone()[0]
    conn.close()

    return render_template('statistics.html', total_tasks=total_tasks, pending_tasks=pending_tasks, in_progress_tasks=in_progress_tasks, completed_tasks=completed_tasks)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
