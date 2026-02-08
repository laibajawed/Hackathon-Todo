"""CLIHandler - Command-line interface for todo application"""

from typing import Optional
from src.manager.todo_manager import TodoManager


class CLIHandler:
    """Command-line interface handler for todo operations."""

    def __init__(self, manager: TodoManager) -> None:
        """Initialize CLIHandler with TodoManager instance.

        Args:
            manager: TodoManager instance for task operations
        """
        self.manager = manager

    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\n=== Todo Manager ===")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark as Complete")
        print("6. Exit")
        print()

    def get_choice(self) -> str:
        """Prompt user for menu choice.

        Returns:
            str: User's menu selection
        """
        return input("Enter your choice (1-6): ").strip()

    def add_task_menu(self) -> None:
        """Handle add task menu option."""
        print("\n--- Add Task ---")

        # Get title
        title = input("Task title (1-200 characters): ").strip()

        # Get optional description
        description_input = input("Task description (optional, press Enter to skip): ").strip()
        description = description_input if description_input else None

        try:
            task = self.manager.add_task(title, description)
            print(f"\n✓ Task created successfully!")
            print(f"  ID: {task.id}")
            print(f"  Title: {task.title}")
            if task.description:
                print(f"  Description: {task.description}")
        except ValueError as e:
            print(f"\n✗ Error: {e}")

    def view_tasks_menu(self) -> None:
        """Handle view tasks menu option."""
        print("\n--- View Tasks ---")

        tasks = self.manager.list_tasks()

        if not tasks:
            print("\nNo tasks found.")
        else:
            for task in tasks:
                status = "[x]" if task.completed else "[ ]"
                print(f"\n{status} ID: {task.id}")
                print(f"    Title: {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
                print(f"    Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        print()

    def update_task_menu(self) -> None:
        """Handle update task menu option."""
        print("\n--- Update Task ---")

        # Get task ID
        task_id_input = input("Enter task ID to update: ").strip()
        try:
            task_id = int(task_id_input)
        except ValueError:
            print("\n✗ Error: Invalid task ID. Please enter a number.")
            return

        # Get new title
        new_title = input("New title (press Enter to keep current): ").strip()

        # Get new description
        new_desc_input = input("New description (press Enter to keep current): ").strip()
        new_description = new_desc_input if new_desc_input else None

        try:
            self.manager.update_task(task_id, new_title or None, new_description)
            print("\n✓ Task updated successfully!")
        except ValueError as e:
            print(f"\n✗ Error: {e}")

    def delete_task_menu(self) -> None:
        """Handle delete task menu option."""
        print("\n--- Delete Task ---")

        # Get task ID
        task_id_input = input("Enter task ID to delete: ").strip()
        try:
            task_id = int(task_id_input)
        except ValueError:
            print("\n✗ Error: Invalid task ID. Please enter a number.")
            return

        deleted = self.manager.delete_task(task_id)
        if deleted:
            print("\n✓ Task deleted successfully!")
        else:
            print("\n✗ Task not found.")

    def toggle_complete_menu(self) -> None:
        """Handle toggle complete menu option."""
        print("\n--- Mark as Complete ---")

        # Get task ID
        task_id_input = input("Enter task ID to toggle completion: ").strip()
        try:
            task_id = int(task_id_input)
        except ValueError:
            print("\n✗ Error: Invalid task ID. Please enter a number.")
            return

        try:
            task = self.manager.toggle_complete(task_id)
            status = "completed" if task.completed else "incomplete"
            print(f"\n✓ Task marked as {status}!")
        except ValueError as e:
            print(f"\n✗ Error: {e}")

    def run(self) -> None:
        """Main application loop.

        Displays menu, gets user choice, executes action, repeats until exit.
        """
        while True:
            self.display_menu()
            choice = self.get_choice()

            if choice == "1":
                self.add_task_menu()
            elif choice == "2":
                self.view_tasks_menu()
            elif choice == "3":
                self.update_task_menu()
            elif choice == "4":
                self.delete_task_menu()
            elif choice == "5":
                self.toggle_complete_menu()
            elif choice == "6":
                print("\nGoodbye!")
                break
            else:
                print("\n✗ Invalid choice. Please enter 1-6.")
