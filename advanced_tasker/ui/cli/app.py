from tkinter import messagebox
from core.database import delete_task, init_db, add_task, get_all_tasks, get_all_categories, add_category
from core.models import Task, Priority
from core.utils import parse_natural_language_date
from datetime import datetime

def print_help():
    print("\nAvailable commands:")
    print("  help    - Show this help")
    print("  add     - Add a new task")
    print("  list    - List all tasks")
    print("  delete  - Delete a task")
    print("  cats    - List all categories")
    print("  exit    - Exit the program\n")

def run_cli():
    init_db()
    print("Advanced Tasker System - CLI Mode")
    print("Type 'help' for commands")
    
    while True:
        try:
            command = input("> ").strip().lower()
            
            if command == 'help':
                print_help()
            elif command == 'add':
                add_task_cli()
            elif command == 'list':
                list_tasks_cli()
            elif command == 'cats':
                list_categories_cli()
            elif command == 'delete':
                delete_task_cli()
            elif command == 'exit':
                break

            else:
                print("Unknown command. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the program")
        except Exception as e:
            print(f"Error: {str(e)}")

def list_categories_cli():
    categories = get_all_categories()
    print("\nAvailable Categories:")
    for cat in categories:
        print(f" - {cat}")

def add_task_cli():
    print("\nAdd New Task")
    print("------------")
    task = Task()
    task.title = input("Task title: ").strip()
    while not task.title:
        print("Title cannot be empty!")
        task.title = input("Task title: ").strip()
    
    task.description = input("Description (optional): ").strip()
    
    # Category selection
    print("\nAvailable categories:")
    categories = get_all_categories()
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    print("0. Add new category")
    
    while True:
        try:
            choice = input("Select category (number) or 0 to add new: ")
            if choice == '0':
                new_cat = input("Enter new category name: ").strip().lower()
                if new_cat:
                    if add_category(new_cat):
                        task.category = new_cat
                        break
                    else:
                        print("Category already exists!")
                else:
                    print("Category name cannot be empty!")
            else:
                selected = int(choice) - 1
                if 0 <= selected < len(categories):
                    task.category = categories[selected]
                    break
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number")

    print("\nPriority levels: 1-Low, 2-Medium, 3-High, 4-Critical")
    while True:
        try:
            priority = int(input("Priority (1-4): "))
            if 1 <= priority <= 4:
                task.priority = Priority(priority)
                break
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    due_date = input("\nDue date (e.g., 'tomorrow 2pm' or '2023-12-31', leave blank if none): ").strip()
    if due_date:
        task.due_date = parse_natural_language_date(due_date)
        if not task.due_date:
            print("Warning: Couldn't understand that date format")
        else:
            print(f"Interpreted due date as: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
    
    task_id = add_task(task)
    print(f"\nTask added successfully with ID: {task_id}\n")

def delete_task_cli():
    list_tasks_cli()  # Show tasks first
    try:
        task_id = int(input("\nEnter ID of task to delete: "))
        if messagebox.askyesno("Confirm", f"Delete task {task_id}? This cannot be undone!"):
            if delete_task(task_id):
                print(f"Task {task_id} deleted successfully")
            else:
                print(f"Failed to delete task {task_id}")
    except ValueError:
        print("Please enter a valid task ID")
        
def list_tasks_cli():
    tasks = get_all_tasks()
    if not tasks:
        print("\nNo tasks found!\n")
        return
    
    print("\nTask List")
    print("---------")
    for task in tasks:
        status = "✓" if task.completed else "✗"
        priority = task.priority.name.ljust(8)
        category = task.category.capitalize().ljust(8)
        
        print(f"{task.id}: {task.title}")
        print(f"  {status} {priority} {category}")
        if task.description:
            print(f"  Description: {task.description}")
        if task.due_date:
            print(f"  Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        print()