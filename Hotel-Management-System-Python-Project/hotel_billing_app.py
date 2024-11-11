from loguru import logger
import pymysql

class MyHotel:
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
        self._create_customers_table()
        self._create_orders_table()
        self._create_feedback_table()

    def _create_customers_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                address VARCHAR(255),
                phone_number VARCHAR(15),
                credits INT DEFAULT 0
            )
        """)
        self.db_connection.commit()

    def _create_orders_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                item_name VARCHAR(50),
                quantity INT,
                price INT,
                order_type VARCHAR(20),
                FOREIGN KEY (customer_id) REFERENCES Customers(id)
            )
        """)
        self.db_connection.commit()

    def _create_feedback_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                stars INT,
                tip INT,
                feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES Customers(id)
            )
        """)
        self.db_connection.commit()

    def get_customer(self, customer_id):
        self.cursor.execute("SELECT * FROM Customers WHERE id = %s", (customer_id,))
        return self.cursor.fetchone()

    def update_customer_credits(self, customer_id, credits):
        self.cursor.execute("UPDATE Customers SET credits = credits + %s WHERE id = %s", (credits, customer_id))
        self.db_connection.commit()

    def calculate_item_price(self, quantity, price_per_item):
        return quantity * price_per_item

    def save_order(self, customer_id, item_name, quantity, price, order_type):
        self.cursor.execute(
            "INSERT INTO Orders (customer_id, item_name, quantity, price, order_type) VALUES (%s, %s, %s, %s, %s)",
            (customer_id, item_name, quantity, price, order_type)
        )
        self.db_connection.commit()
        logger.info(f"Order saved: {item_name}, Quantity: {quantity}, Price: {price}, Type: {order_type}")

    def save_feedback(self, customer_id, stars, tip):
        self.cursor.execute(
            "INSERT INTO Feedback (customer_id, stars, tip) VALUES (%s, %s, %s)",
            (customer_id, stars, tip)
        )
        self.db_connection.commit()
        logger.info(f"Feedback saved: Stars: {stars}, Tip: {tip}")

    def display_menu(self, order_type, customer_id):
        items = self.get_menu_items(order_type)
        total = 0
        logger.info(f"### {order_type} Menu")

        available_credits = self.get_customer_credits(customer_id)
        logger.info(f"Available credits: Rs. {available_credits}")

        total = self.process_order(order_type, customer_id, items, total)

        total = self.apply_credits(available_credits, total, customer_id)

        logger.info(f"#### Total Bill: Rs. {total}")
        self.add_visit_credits(customer_id)
        logger.info("50 credits added for the visit.")

        return total

    def get_menu_items(self, order_type):
        items = {
            'Breakfast': {
                'Idly': 5, 'Vada': 10, 'Dosa': 20, 'Chapathi': 15, 'Puri': 20, 'Parota': 25
            },
            'Lunch': {
                'Meals': 50, 'Veg Rice': 40, 'Gobi': 60, 'Gobi Rice': 50, 'Chapathi': 10, 'Parota': 15
            }
        }
        return items.get(order_type, {})

    def get_customer_credits(self, customer_id):
        self.cursor.execute("SELECT credits FROM Customers WHERE id = %s", (customer_id,))
        return self.cursor.fetchone()[0]

    def process_order(self, order_type, customer_id, items, total):
        for item, price in items.items():
            quantity = int(input(f"Enter number of {item}: "))
            if quantity > 0:
                item_price = self.calculate_item_price(quantity, price)
                total += item_price
                self.save_order(customer_id, item, quantity, item_price, order_type)
                logger.info(f"{item} amount: {item_price}")
        return total

    def apply_credits(self, available_credits, total, customer_id):
        if available_credits > 0:
            if available_credits >= total:
                total = 0
                self.update_customer_credits(customer_id, -available_credits)
                logger.info(f"Credits applied: Rs. {available_credits}. No balance to pay.")
            else:
                total -= available_credits
                self.update_customer_credits(customer_id, -available_credits)
                logger.info(f"Credits applied: Rs. {available_credits}. Remaining balance: Rs. {total}")
        else:
            logger.info(f"No credits available for customer ID {customer_id}. Full amount to pay: Rs. {total}")
        return total

    def add_visit_credits(self, customer_id):
        self.update_customer_credits(customer_id, 50)

    def collect_feedback(self, customer_id):
        logger.info("### Feedback")
        stars = int(input("How many stars would you give? (0-5): "))
        tip = int(input("Enter tip amount (if any): "))
        self.save_feedback(customer_id, stars, tip)
        logger.info(f"Feedback saved! Stars: {stars}, Tip: Rs. {tip}")
        self.handle_feedback(stars)

    def handle_feedback(self, stars):
        feedback_messages = {
            5: "Thank you! Very good maintenance.",
            4: "Thank you! Very good maintenance.",
            3: "Good maintenance.",
            2: "Average maintenance.",
            1: "Very bad maintenance.",
            0: "No feedback given."
        }
        logger.info(feedback_messages.get(stars, "Invalid star rating."))

    def create_customer(self, name, address, phone_number):
        self.cursor.execute(
            "INSERT INTO Customers (name, address, phone_number) VALUES (%s, %s, %s)",
            (name, address, phone_number)
        )
        self.db_connection.commit()
        logger.info(f"Customer created: {name}, {address}, {phone_number}")
        return self.cursor.lastrowid

    def find_customer_by_name_and_phone(self, name, phone_number):
        self.cursor.execute(
            "SELECT * FROM Customers WHERE name = %s AND phone_number = %s", (name, phone_number)
        )
        return self.cursor.fetchone()


# Main function for interaction
if __name__ == "__main__":
    logger.info("Welcome to Hotel Manasa")

    # Get database connection details from the user
    host = input("Enter database host (e.g., 'localhost'): ")
    user = input("Enter database username: ")
    password = input("Enter database password: ")
    db_name = input("Enter database name (default: 'hotel_db'): ") or 'hotel_db'

    # Initialize the MyHotel class with user-provided connection details
    hotel = MyHotel(host, user, password, db_name)

    # Find or create a customer
    customer_name = input("Enter customer name: ")
    customer_phone = input("Enter customer phone number: ")

    # Search for the customer
    customer = hotel.find_customer_by_name_and_phone(customer_name, customer_phone)
    if customer:
        logger.info(f"Customer found: {customer_name}, {customer_phone}, Current credits: Rs. {customer[4]}")
        customer_id = customer[0]
    else:
        customer_address = input("Enter customer address: ")
        customer_id = hotel.create_customer(customer_name, customer_address, customer_phone)

    order_type = input("Select Order Type (Breakfast or Lunch): ")
    if order_type not in ['Breakfast', 'Lunch']:
        logger.error("Invalid order type selected!")
    else:
        total = hotel.display_menu(order_type, customer_id)
        logger.info(f"The total Hotel bill is: Rs. {total}")

        feedback_section = input("Would you like to give feedback? (Yes/No): ")
        if feedback_section.lower() == 'yes':
            hotel.collect_feedback(customer_id)
