from loguru import logger
import os
import shutil

# Configure Loguru
logger.add("system_cleaner.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip")


def get_directory_size(directory):
    """Calculate the total size of files in a directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def clear_directory(directory):
    """Clear the specified directory, skipping files in use."""
    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist.")
        return 0

    cleared_size = 0

    for dirpath, dirnames, filenames in os.walk(directory):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            try:
                if os.path.isfile(filepath):
                    cleared_size += os.path.getsize(filepath)
                    os.remove(filepath)
            except PermissionError:
                logger.warning(f"Permission denied: {filepath}")
            except OSError as e:
                if e.errno == 32:  # File in use
                    logger.warning(f"File in use, skipping: {filepath}")
                else:
                    logger.error(f"Failed to delete file {filepath}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error deleting file {filepath}: {e}")

        for dirname in dirnames:
            dirpath = os.path.join(directory, dirname)
            try:
                shutil.rmtree(dirpath)
                cleared_size += get_directory_size(dirpath)
            except PermissionError:
                logger.warning(f"Permission denied: {dirpath}")
            except OSError as e:
                if e.errno == 32:  # Directory in use
                    logger.warning(f"Directory in use, skipping: {dirpath}")
                else:
                    logger.error(f"Failed to delete directory {dirpath}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error deleting directory {dirpath}: {e}")

    logger.info(f"Cleared {cleared_size / (1024 ** 2):.2f} MB from {directory}.")
    return cleared_size


def main():
    # List of directories to clean
    directories_to_clean = [
        "/tmp",  # Temporary files (Linux/Mac)
        "C:\\Windows\\Temp",  # Temporary files (Windows)
        os.path.expanduser("~/.cache")  # User cache directory
    ]

    total_space_cleared = 0
    for directory in directories_to_clean:
        logger.info(f"Cleaning {directory}...")
        space_cleared = clear_directory(directory)
        if space_cleared > 0:
            logger.info(f"Cleared {space_cleared / (1024 ** 2):.2f} MB from {directory}.")
            total_space_cleared += space_cleared
        else:
            logger.info(f"No space cleared from {directory}.")

    logger.info(f"Total space cleared: {total_space_cleared / (1024 ** 2):.2f} MB.")


if __name__ == "__main__":
    main()
