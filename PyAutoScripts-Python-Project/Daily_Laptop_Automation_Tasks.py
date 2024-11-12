import os
import subprocess
import time
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def open_teams():
    try:
        teams_path = os.getenv("TEAMS_PATH")
        subprocess.Popen(teams_path, shell=True)
        logger.info("Teams opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open Microsoft Teams: {e}")

def open_file_manager():
    try:
        subprocess.Popen('explorer')
        logger.info("File Explorer opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open File Manager: {e}")

def open_powershell():
    try:
        powershell_path = os.getenv("POWERSHELL_PATH")
        subprocess.Popen(powershell_path)
        logger.info("Powershell opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open PowerShell: {e}")

def open_notepad_with_recent():
    try:
        folder_path = os.getenv("NOTEPAD_FOLDER_PATH")
        aws_credentials_path = os.getenv("AWS_CREDENTIALS_PATH")
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        full_paths = [os.path.join(folder_path, f) for f in files]
        full_paths.append(aws_credentials_path)

        for file_path in full_paths:
            subprocess.Popen(['notepad.exe', file_path])
        logger.info("Notepad opened successfully.")

    except Exception as e:
        logger.debug(f"Failed to open Notepad with recent files: {e}")

def open_windows_mail():
    try:
        subprocess.Popen('start outlookmail:', shell=True)
        logger.info("Outlook opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open Windows Mail: {e}")

def open_firefox():
    try:
        firefox_path = os.getenv("FIREFOX_PATH")
        subprocess.Popen(firefox_path)
        logger.info("Firefox opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open Firefox: {e}")

def open_edge():
    try:
        edge_path = os.getenv("EDGE_PATH")
        subprocess.Popen(edge_path)
        logger.info("Edge Browser opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open Edge: {e}")

def snipping_tool():
    try:
        subprocess.Popen('snippingtool')
        logger.info("Snipping Tool opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open Snipping Tool: {e}")

def open_dbeaver():
    try:
        dbeaver_path = os.getenv("DBEAVER_PATH")
        subprocess.Popen(dbeaver_path)
        logger.info("DBeaver app opened successfully.")
    except Exception as e:
        logger.debug(f"Failed to open DBeaver: {e}")

if __name__ == "__main__":
    open_teams()
    time.sleep(2)

    open_file_manager()
    time.sleep(1)

    open_powershell()
    time.sleep(1)

    open_notepad_with_recent()
    time.sleep(1)

    open_windows_mail()
    time.sleep(1)

    open_firefox()
    time.sleep(1)

    open_edge()
    time.sleep(1)

    snipping_tool()
    time.sleep(1)

    open_dbeaver()
    time.sleep(1)

logger.info("DAILY AUTOMATION TASKS EXECUTION COMPLETED")
logger.success("***** Thank You, The Developer *****")
