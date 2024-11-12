import re
import pymysql
from loguru import logger

class ATMSystem:
    def __init__(self, host, user, password, db_name):
        self.db_name = db_name
        self.host = host
        self.user = user
        self.password = password
        self.db_connection = self.connect_to_db()
        self.cursor = self.db_connection.cursor()
        self.create_tables()

    def connect_to_db(self):
        connection = pymysql.connect(
            host=self.host, user=self.user, password=self.password
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        cursor.execute(f"USE {self.db_name}")
        connection.commit()
        return connection

    def create_tables(self):
        self._create_users_table()
        self._create_transactions_table()

    def _create_users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                account_number VARCHAR(20) UNIQUE,
                phone_number VARCHAR(15),
                pin INT(4),
                balance DECIMAL(10, 2) DEFAULT 0.00,
                ifsc_code VARCHAR(11),
                cif VARCHAR(20) UNIQUE,
                gender ENUM('Male', 'Female', 'Other'),
                dob DATE,
                occupation VARCHAR(30) 
            )
        """)
        self.db_connection.commit()

    def _create_transactions_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                type ENUM('Deposit', 'Withdraw') NOT NULL,
                amount DECIMAL(10, 2),
                transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        """)
        self.db_connection.commit()

    def validate_phone_number(self, phone_number):
        return len(phone_number) in range(10, 13) and phone_number.isdigit()

    def validate_dob(self, dob):
        return re.match(r"^\d{4}-\d{2}-\d{2}$", dob)

    def format_gender(self, gender):
        valid_genders = {"male": "Male", "female": "Female", "other": "Other"}
        return valid_genders.get(gender.lower())

    def create_user(self, name, phone_number, pin, gender, dob, occupation):
        # Validate phone number
        if not self.validate_phone_number(phone_number):
            logger.error("Phone number must be between 10 and 12 digits.")
            return None

        # Validate date of birth
        if not self.validate_dob(dob):
            logger.error("Date of birth must be in the format YYYY-MM-DD.")
            return None

        # Format gender
        gender = self.format_gender(gender)
        if gender is None:
            logger.error("Gender must be Male, Female, or Other.")
            return None

        account_number = "SBI0933" + phone_number[-6:]
        ifsc_code = "SBI0000933"
        cif = f"CIF{phone_number[-4:]}{account_number[-4:]}"
        self.cursor.execute(
            "INSERT INTO Users (name, account_number, phone_number, pin, ifsc_code, cif, gender, dob, occupation) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (name, account_number, phone_number, pin, ifsc_code, cif, gender, dob, occupation)
        )
        self.db_connection.commit()
        logger.info(
            f"User created: {name}, Account Number: {account_number}, IFSC Code: {ifsc_code}, CIF: {cif}, DOB: {dob}")
        return self.cursor.lastrowid, account_number

    def authenticate_user(self, account_number, pin):
        self.cursor.execute(
            "SELECT * FROM Users WHERE account_number = %s AND pin = %s", (account_number, pin)
        )
        return self.cursor.fetchone()

    def check_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM Users WHERE id = %s", (user_id,))
        balance = self.cursor.fetchone()[0]
        logger.info(f"Balance for User ID {user_id}: Rs. {balance}")
        return balance

    def view_account_details(self, user_id):
        self.cursor.execute("""
            SELECT name, account_number, phone_number, balance, ifsc_code, cif, gender, dob, occupation
            FROM Users
            WHERE id = %s
        """, (user_id,))
        account_details = self.cursor.fetchone()

        if account_details:
            logger.info(f"Account Details for User ID {user_id}:")
            logger.info(f"Name: {account_details[0]}")
            logger.info(f"Account Number: {account_details[1]}")
            logger.info(f"Phone Number: {account_details[2]}")
            logger.info(f"Balance: Rs. {account_details[3]}")
            logger.info(f"IFSC Code: {account_details[4]}")
            logger.info(f"CIF: {account_details[5]}")
            logger.info(f"Gender: {account_details[6]}")
            logger.info(f"Date of Birth: {account_details[7]}")
            logger.info(f"Occupation: {account_details[8]}")
            return account_details
        else:
            logger.error("Account details not found.")
            return None

    def deposit(self, user_id, amount):
        max_attempts = 3  # Maximum number of attempts
        attempts = 0  # Counter for attempts

        while attempts < max_attempts:
            if 1.00 <= amount <= 99999999.99:
                # Valid amount, proceed with the deposit
                self.cursor.execute("UPDATE Users SET balance = balance + %s WHERE id = %s", (amount, user_id))
                self.db_connection.commit()
                self.save_transaction(user_id, 'Deposit', amount)
                logger.info(f"Deposited Rs. {amount} to User ID {user_id}")
                return True
            else:
                # Invalid amount, log an error and prompt again
                logger.error("Invalid deposit amount. Please enter an amount between Rs. 1.00 and Rs. 99999999.99.")
                attempts += 1
                if attempts < max_attempts:
                    # Prompt for a new amount (assuming this is part of a larger interactive system)
                    amount = float(input("Please enter a valid deposit amount: "))

        # If the user fails to enter a valid amount in 3 attempts, return False
        logger.error("Failed to enter a valid deposit amount after 3 attempts.")
        return False

    def withdraw(self, user_id, amount):
        current_balance = self.check_balance(user_id)
        if amount > 0 and current_balance >= amount:
            self.cursor.execute("UPDATE Users SET balance = balance - %s WHERE id = %s", (amount, user_id))
            self.db_connection.commit()
            self.save_transaction(user_id, 'Withdraw', amount)
            logger.info(f"Withdraw Rs. {amount} from User ID {user_id}")
            return True
        else:
            logger.error("Insufficient balance or invalid withdrawal amount.")
            return False

    def save_transaction(self, user_id, transaction_type, amount):
        self.cursor.execute(
            "INSERT INTO Transactions (user_id, type, amount) VALUES (%s, %s, %s)",
            (user_id, transaction_type, amount)
        )
        self.db_connection.commit()
        logger.info(f"Transaction saved: {transaction_type} of Rs. {amount}")

    def view_transaction_history(self, user_id):
        self.cursor.execute("SELECT type, amount, transaction_time FROM Transactions WHERE user_id = %s", (user_id,))
        transactions = self.cursor.fetchall()

        # Fetch the current balance for the user
        self.cursor.execute("SELECT balance FROM Users WHERE id = %s", (user_id,))
        balance_result = self.cursor.fetchone()
        balance = balance_result[0] if balance_result else 0

        for transaction in transactions:
            logger.info(f"{transaction[2]} - {transaction[0]}: Rs. {transaction[1]}")

        # Display the balance at the end of transaction history
        logger.info(f"Current Balance: Rs. {balance}")

        return transactions


# Main function for interaction
if __name__ == "__main__":
    logger.info("Welcome to the SBI Bank ATM System")

    # Get database connection details from the user
    host = input("Enter database host (e.g., 'localhost'): ")
    user = input("Enter database username: ")
    password = input("Enter database password: ")
    db_name = input("Enter database name (default: 'atm_db'): ") or 'atm_db'

    # Initialize the ATMSystem class with user-provided connection details
    atm = ATMSystem(host, user, password, db_name)

    # User authentication
    account_number = input("Enter your account number: ")
    pin = int(input("Enter your PIN: "))

    # Authenticate user or create a new one if not found
    user = atm.authenticate_user(account_number, pin)
    if user:
        user_id = user[0]
        logger.info(f"Welcome, {user[1]}!")
    else:
        logger.info("No account found with the given details.")
        create_new = input("Would you like to create a new account? (yes/no): ")
        if create_new.lower() == 'yes':
            name = input("Enter your name: ")
            phone_number = input("Enter your phone number: ")
            pin = input("Set a 4-digit PIN: ")
            gender = input("Enter your gender (Male/Female/Other): ")
            dob = input("Enter your date of birth (YYYY-MM-DD): ")
            occupation = input("Enter your present occupation (work name) : ")
            user_id, new_account_number = atm.create_user(name, phone_number, pin, gender, dob, occupation)
            logger.info(f"Account created successfully! Your new account number is {new_account_number}")
        else:
            logger.info("Exiting system. Thank you!")
            exit()

    # Options for ATM services
    while True:
        print("\nSelect an option:")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. View Transaction History")
        print("5. View Account Details")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            atm.check_balance(user_id)
        elif choice == '2':
            amount = float(input("Enter deposit amount: "))
            atm.deposit(user_id, amount)
        elif choice == '3':
            amount = float(input("Enter withdrawal amount: "))
            atm.withdraw(user_id, amount)
        elif choice == '4':
            atm.view_transaction_history(user_id)
        elif choice == '5':
            atm.view_account_details(user_id)
        elif choice == '6':
            logger.success("Thank you for using the ATM system!")
            break
        else:
            logger.error("Invalid choice. Please try again.")
