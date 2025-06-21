import sqlite3
from pathlib import Path
from datetime import datetime
from .models import Task, Priority

DB_PATH = Path.home() / ".advanced_tasker" / "tasks.db"

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        priority INTEGER,
        due_date TEXT,
        created_at TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        recurring INTEGER DEFAULT 0,
        recurrence_pattern TEXT,
        time_spent INTEGER DEFAULT 0
    )
    """)
    
    default_categories = ['work', 'personal', 'family']
    for category in default_categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    
    conn.commit()
    conn.close()


def update_task_status(task_id, completed):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", 
                     (1 if completed else 0, task_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating task status: {e}")
        return False
    finally:
        conn.close()

def delete_task(task_id):
    """Delete a task from the database by its ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # First delete any attachments
        cursor.execute("DELETE FROM attachments WHERE task_id = ?", (task_id,))
        # Then delete the task
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0  # Returns True if a task was deleted
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False
    finally:
        conn.close()
        
def clear_completed_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE completed = 1")
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Error clearing completed tasks: {e}")
        return 0
    finally:
        conn.close()

def get_all_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def add_category(category_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name.lower(),))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def add_task(task):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO tasks (
        title, description, category, priority, due_date, 
        created_at, completed, recurring, recurrence_pattern, time_spent
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.title, task.description, task.category, task.priority.value,
        task.due_date.isoformat() if task.due_date else None,
        task.created_at.isoformat(), task.completed, task.recurring,
        task.recurrence_pattern, task.time_spent
    ))
    
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_all_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, title, description, category, priority, due_date, 
           created_at, completed, recurring, recurrence_pattern, time_spent
    FROM tasks
    ORDER BY priority DESC, due_date ASC
    """)
    
    tasks = []
    for row in cursor.fetchall():
        task = Task()
        task.id = row[0]
        task.title = row[1]
        task.description = row[2]
        task.category = row[3]
        task.priority = Priority(row[4])
        task.due_date = datetime.fromisoformat(row[5]) if row[5] else None
        task.created_at = datetime.fromisoformat(row[6])
        task.completed = bool(row[7])
        task.recurring = bool(row[8])
        task.recurrence_pattern = row[9]
        task.time_spent = row[10]
        tasks.append(task)
    
    conn.close()
    return tasks