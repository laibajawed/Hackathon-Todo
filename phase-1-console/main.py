"""Phase I Console Todo Application - Main Entry Point"""

from src.manager.todo_manager import TodoManager
from src.cli.handler import CLIHandler


def main() -> None:
    """Main application entry point.

    Initializes TodoManager and CLIHandler, then runs the main loop.
    """
    manager = TodoManager()
    handler = CLIHandler(manager)
    handler.run()


if __name__ == "__main__":
    main()
