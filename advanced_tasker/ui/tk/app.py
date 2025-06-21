import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from core.database import DB_PATH, init_db, add_task, get_all_tasks, get_all_categories, add_category, update_task_status
from core.models import Task, Priority
from core.utils import parse_natural_language_date
import sqlite3
from core.database import (init_db, add_task, get_all_tasks, 
                         get_all_categories, add_category, 
                         update_task_status, delete_task)

class TaskerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Tasker System")
        self.root.geometry("1000x600")
        
        init_db()
        
        # Create container frame
        self.container = ttk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create both frames but don't show them yet
        self.create_progress_frame()
        self.create_done_frame()
        
        # Show the progress frame by default
        self.show_progress_frame()
    
    def create_progress_frame(self):
        self.progress_frame = ttk.Frame(self.container)
        
        # Add Task Frame
        add_frame = ttk.LabelFrame(self.progress_frame, text="Add New Task", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Task Title
        ttk.Label(add_frame, text="Title:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(add_frame, width=50)
        self.title_entry.grid(row=0, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=2)
        
        # Description
        ttk.Label(add_frame, text="Description:").grid(row=1, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(add_frame, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=2)
        
        # Category
        ttk.Label(add_frame, text="Category:").grid(row=2, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(add_frame, textvariable=self.category_var)
        self.category_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Add category button
        self.new_cat_btn = ttk.Button(add_frame, text="+", width=3,
                                    command=self.add_new_category)
        self.new_cat_btn.grid(row=2, column=2, sticky=tk.W, padx=0)
        
        # Priority
        ttk.Label(add_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W)
        self.priority_var = tk.IntVar(value=2)
        priorities = [("Low", 1), ("Medium", 2), ("High", 3), ("Critical", 4)]
        for i, (text, val) in enumerate(priorities):
            rb = ttk.Radiobutton(add_frame, text=text, value=val, variable=self.priority_var)
            rb.grid(row=3, column=i+1, sticky=tk.W, padx=5, pady=2)
        
        # Due Date
        ttk.Label(add_frame, text="Due Date:").grid(row=4, column=0, sticky=tk.W)
        self.due_entry = ttk.Entry(add_frame, width=30)
        self.due_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(add_frame, text="(e.g., 'tomorrow 2pm' or '2023-12-31')").grid(row=4, column=2, columnspan=2, sticky=tk.W)
        
        # Add Button
        add_btn = ttk.Button(add_frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=5, column=3, sticky=tk.E, pady=5)
        delete_btn = ttk.Button(nav_frame, text="Delete Selected", command=self.delete_selected_task)
        delete_btn.pack(side=tk.LEFT, padx=5)
        # Task List Frame
        list_frame = ttk.LabelFrame(self.progress_frame, text="Tasks In Progress", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for tasks
        columns = ("id", "title", "category", "priority", "due_date", "completed")
        self.progress_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configure columns
        self.progress_tree.heading("id", text="ID")
        self.progress_tree.heading("title", text="Title")
        self.progress_tree.heading("category", text="Category")
        self.progress_tree.heading("priority", text="Priority")
        self.progress_tree.heading("due_date", text="Due Date")
        self.progress_tree.heading("completed", text="Done")
        
        self.progress_tree.column("id", width=50, anchor=tk.CENTER)
        self.progress_tree.column("title", width=200)
        self.progress_tree.column("category", width=100)
        self.progress_tree.column("priority", width=80)
        self.progress_tree.column("due_date", width=120)
        self.progress_tree.column("completed", width=50, anchor=tk.CENTER)
        
        self.progress_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.progress_tree.yview)
        self.progress_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.progress_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        view_done_btn = ttk.Button(nav_frame, text="View Completed Tasks", 
                                 command=self.show_done_frame)
        view_done_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_done_frame(self):
        self.done_frame = ttk.Frame(self.container)
        
        # Task List Frame
        list_frame = ttk.LabelFrame(self.done_frame, text="Completed Tasks", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for completed tasks
        columns = ("id", "title", "category", "priority", "due_date", "completed")
        self.done_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configure columns
        self.done_tree.heading("id", text="ID")
        self.done_tree.heading("title", text="Title")
        self.done_tree.heading("category", text="Category")
        self.done_tree.heading("priority", text="Priority")
        self.done_tree.heading("due_date", text="Due Date")
        self.done_tree.heading("completed", text="Done")
        
        self.done_tree.column("id", width=50, anchor=tk.CENTER)
        self.done_tree.column("title", width=200)
        self.done_tree.column("category", width=100)
        self.done_tree.column("priority", width=80)
        self.done_tree.column("due_date", width=120)
        self.done_tree.column("completed", width=50, anchor=tk.CENTER)
        
        self.done_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.done_tree.yview)
        self.done_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.done_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        view_progress_btn = ttk.Button(nav_frame, text="Back to Tasks In Progress", 
                                    command=self.show_progress_frame)
        view_progress_btn.pack(side=tk.LEFT, padx=5)
        
        clear_completed_btn = ttk.Button(nav_frame, text="Clear Completed Tasks",
                                    command=self.clear_completed_tasks)
        clear_completed_btn.pack(side=tk.RIGHT, padx=5)
        
        delete_done_btn = ttk.Button(nav_frame, text="Delete Selected",
                               command=self.delete_selected_done_task)
        delete_done_btn.pack(side=tk.LEFT, padx=5)
        
        # Add click handler for the done tree
        self.done_tree.bind("<Button-1>", self.on_done_task_click)

    def on_done_task_click(self, event):
        region = self.done_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.done_tree.identify_column(event.x)
            item = self.done_tree.identify_row(event.y)
            
            if column == "#6":  # Completed column
                task_id = self.done_tree.item(item, "values")[0]
                if update_task_status(task_id, False):  # Set to not completed
                    self.refresh_done_tasks()
                    self.refresh_progress_tasks()
                    messagebox.showinfo("Success", "Task moved back to In Progress")
                    
    def show_progress_frame(self):
        self.done_frame.pack_forget()
        self.progress_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_categories()
        self.refresh_progress_tasks()
    
    def show_done_frame(self):
        self.progress_frame.pack_forget()
        self.done_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_done_tasks()
    
    def refresh_categories(self):
        self.categories = get_all_categories()
        self.category_combo['values'] = self.categories
        if self.categories:
            self.category_var.set(self.categories[0])
    
    def refresh_progress_tasks(self):
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)
        
        tasks = get_all_tasks()
        for task in tasks:
            if not task.completed:
                due_date = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else ""
                
                item = self.progress_tree.insert("", tk.END, values=(
                    task.id,
                    task.title,
                    task.category.capitalize(),
                    task.priority.name,
                    due_date,
                    "✓" if task.completed else "✗"
                ))
                
                # Tag completed items differently
                tags = ("completed",) if task.completed else ()
                self.progress_tree.item(item, tags=tags)
        
        # Add checkbox functionality
        self.progress_tree.tag_configure("completed", foreground="gray")
        self.progress_tree.bind("<Button-1>", self.on_task_click)
    
    def refresh_done_tasks(self):
        for item in self.done_tree.get_children():
            self.done_tree.delete(item)
        
        tasks = get_all_tasks()
        for task in tasks:
            if task.completed:
                due_date = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else ""
                
                item = self.done_tree.insert("", tk.END, values=(
                    task.id,
                    task.title,
                    task.category.capitalize(),
                    task.priority.name,
                    due_date,
                    "✓"
                ))
                
                # Tag items for visual consistency
                self.done_tree.item(item, tags=("completed",))
        
        # Style for completed tasks
        self.done_tree.tag_configure("completed", foreground="gray")
    
    def on_task_click(self, event):
        region = self.progress_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.progress_tree.identify_column(event.x)
            item = self.progress_tree.identify_row(event.y)
            
            if column == "#6":  # Completed column
                task_id = self.progress_tree.item(item, "values")[0]
                current_status = self.progress_tree.item(item, "values")[5] == "✓"
                new_status = not current_status
                
                if update_task_status(task_id, new_status):
                    self.refresh_progress_tasks()
                    self.refresh_done_tasks()
    
    def add_new_category(self):
        new_cat = simpledialog.askstring("New Category", "Enter new category name:")
        if new_cat and new_cat.strip():
            new_cat = new_cat.strip().lower()
            if add_category(new_cat):
                self.refresh_categories()
                self.category_var.set(new_cat)
                messagebox.showinfo("Success", f"Category '{new_cat}' added!")
            else:
                messagebox.showerror("Error", "Category already exists!")
    
    def add_task(self):
        task = Task()
        task.title = self.title_entry.get().strip()
        if not task.title:
            messagebox.showerror("Error", "Task title cannot be empty!")
            return
        
        task.description = self.desc_entry.get().strip()
        task.category = self.category_var.get().lower()
        if not task.category:
            messagebox.showerror("Error", "Please select a category!")
            return
        
        task.priority = Priority(self.priority_var.get())
        
        due_date = self.due_entry.get().strip()
        if due_date:
            task.due_date = parse_natural_language_date(due_date)
            if not task.due_date:
                messagebox.showwarning("Warning", "Couldn't understand the date format")
        
        try:
            task_id = add_task(task)
            messagebox.showinfo("Success", f"Task added with ID: {task_id}")
            self.clear_form()
            self.refresh_progress_tasks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {str(e)}")
    
    def clear_completed_tasks(self):
        if messagebox.askyesno("Confirm", "Delete all completed tasks?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE completed = 1")
            conn.commit()
            conn.close()
            self.refresh_done_tasks()
            self.refresh_progress_tasks()
            
    def delete_selected_task(self):
        selected = self.progress_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
        
        task_id = self.progress_tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm Delete", 
                            f"Delete task {task_id}? This cannot be undone!"):
            if delete_task(task_id):
                self.refresh_progress_tasks()
                messagebox.showinfo("Success", f"Task {task_id} deleted")
            else:
                messagebox.showerror("Error", f"Failed to delete task {task_id}")

    def delete_selected_done_task(self):
        selected = self.done_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
        
        task_id = self.done_tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm Delete", 
                            f"Delete task {task_id}? This cannot be undone!"):
            if delete_task(task_id):
                self.refresh_done_tasks()
                messagebox.showinfo("Success", f"Task {task_id} deleted")
            else:
                messagebox.showerror("Error", f"Failed to delete task {task_id}")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.priority_var.set(2)
        self.due_entry.delete(0, tk.END)

def run_tk_app():
    root = tk.Tk()
    app = TaskerApp(root)
    root.mainloop()