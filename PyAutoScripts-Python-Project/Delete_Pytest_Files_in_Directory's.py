import os
import shutil
from loguru import logger

# Set up loguru to log to a file
logger.add("cleanup.log", rotation="500 KB", retention="10 days")


def remove_test_artifacts(directory_path):
    # Define the files and directories to remove
    items_to_remove = ['.coverage', '.pytest_cache', '__pycache__', 'htmlcov', '*.pyc']

    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory_path):
        # Check for the files to remove
        for file in files:
            if file in items_to_remove or file.endswith(".pyc"):
                file_path = os.path.join(root, file)
                try:
                    logger.info(f"Removing file: {file_path}")
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to remove file: {file_path}. Error: {e}")

        # Check for the directories to remove
        for dir_name in dirs:
            if dir_name in items_to_remove:
                dir_path = os.path.join(root, dir_name)
                try:
                    logger.info(f"Removing directory: {dir_path}")
                    shutil.rmtree(dir_path)
                except Exception as e:
                    logger.error(f"Failed to remove directory: {dir_path}. Error: {e}")


if __name__ == "__main__":
    while True:
        directory_path = input("Enter the full directory path to delete pytest cache files: ").strip()
        if not os.path.isdir(directory_path):
            logger.error(f"The directory path {directory_path} does not exist. Please provide a valid path.")
            continue

        user_decision = input("Do you want to proceed to delete (Y/n): ").strip()
        if user_decision.lower() == "y":
            remove_test_artifacts(directory_path)
            logger.info("PyTest files cleanup complete.")
        else:
            logger.info("Deletion process not authorized. Thank you.")

        run_again = input("Do you want to run another directory? (Y/n): ").strip().lower()
        if run_again != 'y':
            logger.info("Exiting the program.")
            break
