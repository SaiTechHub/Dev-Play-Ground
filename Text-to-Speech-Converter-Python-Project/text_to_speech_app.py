import os
from loguru import logger
import pyttsx3
import platform

class TextToSpeech:
    def __init__(self, engine="pyttsx3"):
        self.engine = engine
        if engine == "pyttsx3":
            self.tts_engine = pyttsx3.init()
            logger.info("Initialized pyttsx3 engine.")
        elif engine == "gTTS":
            logger.info("Using gTTS for text-to-speech.")
        else:
            logger.error("Invalid engine specified. Choose 'pyttsx3' or 'gTTS'.")
            raise ValueError("Invalid engine specified.")

    def get_downloads_folder(self):
        """Get the default Downloads folder based on the operating system."""
        if platform.system() == "Windows":
            return os.path.join(os.environ["USERPROFILE"], "Downloads")
        elif platform.system() == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Downloads")
        elif platform.system() == "Linux":
            return os.path.join(os.path.expanduser("~"), "Downloads")
        else:
            logger.error("Unsupported OS.")
            raise EnvironmentError("Unsupported operating system.")

    def text_to_speech(self, text, save_as_file=False, output_file="output.mp3"):
        logger.info("Starting text-to-speech conversion.")
        try:
            logger.info(f"Starting text-to-speech conversion using engine {self.engine}")
            if self.engine == "pyttsx3":
                logger.info("Speaking the following text:")
                print(text)  # Print the text to display while speaking
                self.tts_engine.say(text)

                if save_as_file:
                    download_folder = self.get_downloads_folder()
                    output_path = os.path.join(download_folder, output_file)
                    logger.info(f"Saving output to {output_path}.")
                    self.tts_engine.save_to_file(text, output_path)

                self.tts_engine.runAndWait()

            logger.info("Text-to-speech conversion completed.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

    def text_file_to_speech(self, file_path, save_as_file=False, output_file="audiobook.mp3"):
        if not os.path.exists(file_path):
            logger.error(f"The file {file_path} does not exist.")
            raise FileNotFoundError(f"{file_path} not found.")

        logger.info(f"Reading text from {file_path}.")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            logger.info("Converting text from file to speech.")
            self.text_to_speech(text, save_as_file, output_file)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise


def main():
    logger.info("Welcome to the Text-to-Speech Converter.")
    tts = TextToSpeech(engine="pyttsx3")

    choice = input("Do you want to convert input text or a file? (Enter 'text' or 'file'): ").strip().lower()

    if choice == 'text':
        text = input("Enter the text you want to convert to speech: ")
        save_choice = input("Do you want to save the speech as a file? (yes/no): ").strip().lower()
        if save_choice == 'yes':
            output_file = input("Enter the output file name (e.g., output.mp3): ")
            tts.text_to_speech(text, save_as_file=True, output_file=output_file)
        else:
            tts.text_to_speech(text, save_as_file=False)

    elif choice == 'file':
        file_path = input("Enter the file path to the text file: ")
        save_choice = input("Do you want to save the speech as a file? (yes/no): ").strip().lower()
        if save_choice == 'yes':
            output_file = input("Enter the output file name (e.g., audiobook.mp3): ")
            tts.text_file_to_speech(file_path, save_as_file=True, output_file=output_file)
        else:
            tts.text_file_to_speech(file_path, save_as_file=False)

    else:
        logger.error("Invalid choice! Please enter 'text' or 'file'.")


if __name__ == "__main__":
    main()
