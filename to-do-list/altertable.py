import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('todo_list.db')
c = conn.cursor()

# Agregar la columna 'status' a la tabla 'tasks'
c.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'Pending'")

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()
