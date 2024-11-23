import os
import shutil
from tkinter import Tk, filedialog, messagebox, Button


def organize_files(directory):
    if not os.path.exists(directory):
        messagebox.showerror("Error", "Directory does not exist!")
        return

    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Get the file extension
            _, extension = os.path.splitext(filename)
            extension = extension[1:]  # Remove the dot (e.g., '.jpg' -> 'jpg')

            # Skip files without an extension
            if not extension:
                extension = "Others"

            # Create a folder for the extension if it doesn't exist
            folder_path = os.path.join(directory, extension)
            os.makedirs(folder_path, exist_ok=True)

            # Move the file to the corresponding folder
            shutil.move(file_path, os.path.join(folder_path, filename))

        messagebox.showinfo("Success", "Files organized successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        organize_files(folder)


# Set up the Tkinter GUI
def main():
    root = Tk()
    root.title("File Organizer")

    # Create a button to select a folder
    select_button = Button(root, text="Select Folder to Organize", command=select_folder, padx=20, pady=10)
    select_button.pack(pady=20)

    # Run the Tkinter event loop
    root.geometry("300x150")
    root.mainloop()


if __name__ == "__main__":
    main()
