import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Crear la conexión a la base de datos SQLite
conn = sqlite3.connect('todo_list.db')
c = conn.cursor()

# Crear la tabla de usuarios si no existe
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')

# Crear la tabla de tareas si no existe
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, task TEXT, status TEXT DEFAULT 'Pending')''')

# Crear un usuario predeterminado si no hay usuarios
c.execute("SELECT COUNT(*) FROM users")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
    conn.commit()

conn.commit()

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("600x500")
        self.resizable(False, False)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Iniciar sesión
        self.login_frame = LoginFrame(self.style, self)
        self.login_frame.pack(pady=50)

    def show_todo_frame(self, user_id):
        self.login_frame.destroy()
        self.todo_frame = TodoFrame(self.style, self, user_id)
        self.todo_frame.pack(fill="both", expand=True)

class LoginFrame(tk.Frame):
    def __init__(self, style, master):
        super().__init__(master)
        self.master = master
        self.style = style  # Guardar el estilo pasado

        # Estilos
        self.style.configure("TLabel", font=("Arial", 14))
        self.style.configure("TEntry", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 12))

        # Etiquetas y entradas
        self.username_label = ttk.Label(self, text="Username:")
        self.username_label.pack(pady=10)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(self, text="Password:")
        self.password_label.pack(pady=10)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        # Botón de inicio de sesión
        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Verificar las credenciales en la base de datos
        c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user_id = c.fetchone()

        if user_id:
            self.master.show_todo_frame(user_id[0])
        else:
            messagebox.showerror("Error", "Invalid username or password.")

class TodoFrame(tk.Frame):
    def __init__(self, style, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.style = style  # Guardar el estilo pasado

        # Estilos
        self.style.configure("Treeview", font=("Arial", 12))
        self.style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        # Treeview para mostrar las tareas
        self.tree = ttk.Treeview(self, columns=("Task", "Status", "Actions"), show="headings")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Actions", text="Actions")
        self.tree.column("Task", width=400)
        self.tree.column("Status", width=100)
        self.tree.column("Actions", width=100)
        self.tree.pack(pady=20)

        # Cargar las tareas del usuario desde la base de datos
        self.load_tasks()

        # Entrada para agregar nuevas tareas
        self.task_entry = ttk.Entry(self, font=("Arial", 12))
        self.task_entry.pack(pady=10)

        # Botón para agregar una nueva tarea
        self.add_button = ttk.Button(self, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=10)

        # Botón para eliminar la tarea seleccionada
        self.delete_button = ttk.Button(self, text="Delete Selected Task", command=self.delete_selected_task)
        self.delete_button.pack(pady=10)

    def load_tasks(self):
        # Eliminar las tareas existentes del Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar las tareas del usuario desde la base de datos
        c.execute("SELECT id, task, status FROM tasks WHERE user_id = ?", (self.user_id,))
        tasks = c.fetchall()

        for task_id, task, status in tasks:
            # Insertar la tarea en el Treeview
            self.tree.insert("", "end", iid=task_id, values=(task, status, "Change Status"))

            # Cambiar el color de fondo según el estado
            if status == "Pending":
                self.tree.item(task_id, tags=("pending",))
            elif status == "In Process":
                self.tree.item(task_id, tags=("in_process",))
            elif status == "Finished":
                self.tree.item(task_id, tags=("finished",))

        # Configurar colores de fondo
        self.tree.tag_configure("pending", background="red", foreground="white")
        self.tree.tag_configure("in_process", background="yellow", foreground="black")
        self.tree.tag_configure("finished", background="green", foreground="white")

    def add_task(self):
        task = self.task_entry.get()
        if task:
            # Insertar la nueva tarea en la base de datos
            c.execute("INSERT INTO tasks (user_id, task, status) VALUES (?, ?, ?)", (self.user_id, task, "Pending"))
            conn.commit()
            self.task_entry.delete(0, tk.END)
            self.load_tasks()

    def delete_selected_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = selected_item[0]
            c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "Please select a task to delete.")

    def change_status(self, task_id, new_status):
        c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        self.load_tasks()

    def on_change_status_click(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = selected_item[0]
            current_status = self.tree.item(task_id, "values")[1]
            
            if current_status == "Pending":
                new_status = "In Process"
            elif current_status == "In Process":
                new_status = "Finished"
            elif current_status == "Finished":
                new_status = "Pending"
            
            self.change_status(task_id, new_status)

if __name__ == "__main__":
    try:
        app = TodoApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", str(e))
