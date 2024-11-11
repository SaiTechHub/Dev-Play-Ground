from loguru import logger
import pymysql


class VehicleParkingSystem:
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
        self._create_vehicles_table()

    def _create_customers_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                phone_number VARCHAR(15),
                address VARCHAR(255),
                visit_count INT DEFAULT 0
            )
        """)
        self.db_connection.commit()

    def _create_vehicles_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vehicles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                vehicle_number VARCHAR(50),
                vehicle_type VARCHAR(50),
                parking_duration_days INT,
                total_fee INT,
                FOREIGN KEY (customer_id) REFERENCES Customers(id)
            )
        """)
        self.db_connection.commit()

    def find_customer(self, name, phone_number):
        self.cursor.execute(
            "SELECT id FROM Customers WHERE name = %s AND phone_number = %s", (name, phone_number)
        )
        customer = self.cursor.fetchone()
        if customer:
            return customer[0]  # Return the customer ID
        else:
            logger.error(f"Customer with Name: {name} and Phone: {phone_number} not found.")
            return None

    def register_customer(self, name, phone_number, address):
        self.cursor.execute(
            "INSERT INTO Customers (name, phone_number, address) VALUES (%s, %s, %s)",
            (name, phone_number, address)
        )
        self.db_connection.commit()
        customer_id = self.cursor.lastrowid
        logger.info(f"Customer registered: {name}, Phone: {phone_number}")
        return customer_id

    def register_vehicle(self, customer_id, vehicle_number, vehicle_type):
        if vehicle_type not in ['2-wheeler', '4-wheeler', '6-wheeler']:
            logger.error(f"Invalid vehicle type: {vehicle_type}. Only 2, 4, and 6 wheelers are allowed.")
            return None

        # Check if the vehicle number already exists for the same customer
        self.cursor.execute(
            "SELECT customer_id FROM Vehicles WHERE vehicle_number = %s", (vehicle_number,)
        )
        existing_vehicle = self.cursor.fetchone()

        if existing_vehicle:
            if existing_vehicle[0] == customer_id:
                logger.error(f"Vehicle with number {vehicle_number} already registered for this customer.")
                return vehicle_number
            else:
                logger.info(f"Vehicle number {vehicle_number} already registered for another customer.")
                # Optionally, apply credits for the existing customer, or just return
                return vehicle_number

        fee = self.get_parking_fee(vehicle_type)
        if fee == -1:
            logger.error(f"No fee available for vehicle type: {vehicle_type}")
            return None

        self.cursor.execute(
            "INSERT INTO Vehicles (customer_id, vehicle_number, vehicle_type, parking_duration_days, total_fee) VALUES (%s, %s, %s, %s, %s)",
            (customer_id, vehicle_number, vehicle_type, 1, fee)  # Default parking duration is 1 day
        )
        self.db_connection.commit()
        logger.info(f"Vehicle registered: {vehicle_number}, Type: {vehicle_type}, Fee: {fee}")
        return vehicle_number

    def get_parking_fee(self, vehicle_type):
        fees = {
            '2-wheeler': 20,  # Fee for 2-wheelers (Rs. 20)
            '4-wheeler': 50,  # Fee for 4-wheelers (Rs. 50)
            '6-wheeler': 100  # Fee for 6-wheelers (Rs. 100)
        }
        return fees.get(vehicle_type, -1)

    def update_parking_duration(self, vehicle_number, duration):
        self.cursor.execute(
            "UPDATE Vehicles SET parking_duration_days = %s WHERE vehicle_number = %s", (duration, vehicle_number)
        )
        self.db_connection.commit()
        logger.info(f"Parking duration updated for vehicle Number: {vehicle_number}, Duration: {duration} day(s)")

    def calculate_total_fee(self, vehicle_number, apply_discount=False):
        # Query for the vehicle type and parking duration
        self.cursor.execute("SELECT vehicle_type, parking_duration_days FROM Vehicles WHERE vehicle_number = %s", (vehicle_number,))
        vehicle = self.cursor.fetchone()

        if not vehicle:
            logger.error(f"Vehicle Number {vehicle_number} not found!")
            return None

        # Unpack vehicle data
        print("1")
        vehicle_type, parking_duration = vehicle
        print("2")

        # Get the parking fee for the vehicle type
        fee = self.get_parking_fee(vehicle_type)
        if fee == -1:
            logger.error(f"Invalid vehicle type: {vehicle_type}. Fee not found.")
            return None

        # Calculate total fee
        total_fee = fee * parking_duration

        # Apply discount if applicable
        if apply_discount:
            total_fee *= 0.9  # 10% discount for next visit
            logger.info(f"Discount applied. New total fee: Rs. {total_fee}")

        # Update the total fee in the database
        self.cursor.execute("UPDATE Vehicles SET total_fee = %s WHERE vehicle_number = %s", (total_fee, vehicle_number))
        self.db_connection.commit()
        logger.info(f"Total fee calculated for vehicle ID: {vehicle_number}, Total fee: Rs. {total_fee}")

        return total_fee

    def add_visit_and_credit(self, customer_id, vehicle_type):
        # Get current visit count and increase it by 1
        self.cursor.execute("SELECT visit_count FROM Customers WHERE id = %s", (customer_id,))
        result = self.cursor.fetchone()
        if result:
            visit_count = result[0] + 1
            self.cursor.execute("UPDATE Customers SET visit_count = %s WHERE id = %s", (visit_count, customer_id))
            self.db_connection.commit()
            logger.info(f"Customer ID {customer_id} now has {visit_count} visits.")

            # Add credit based on vehicle type and visits
            credit = 0
            if visit_count == 1:
                if vehicle_type == '2-wheeler':
                    credit = 10
                elif vehicle_type == '4-wheeler':
                    credit = 20
                elif vehicle_type == '6-wheeler':
                    credit = 30
                logger.info(f"Credit added for vehicle type {vehicle_type}: Rs. {credit}")
                return credit
            else:
                logger.info(f"Customer has visited {visit_count} times, no credit added.")
                return 0
        return 0

    def apply_discount_on_next_visit(self, customer_id):
        # Check visit count and apply discount for the next visit
        self.cursor.execute("SELECT visit_count FROM Customers WHERE id = %s", (customer_id,))
        result = self.cursor.fetchone()
        if result and result[0] > 1:
            logger.info(f"Discount will be applied on next visit for customer {customer_id}.")
            return True  # Apply discount logic here
        return False


# Main function for interaction
if __name__ == "__main__":
    logger.info("Welcome to the Vehicle Parking System")

    # Get database connection details from the user
    host = input("Enter database host (e.g., 'localhost'): ")
    user = input("Enter database username: ")
    password = input("Enter database password: ")
    db_name = input("Enter database name (default: 'parking_db'): ") or 'parking_db'

    # Initialize the VehicleParkingSystem class with user-provided connection details
    parking_system = VehicleParkingSystem(host, user, password, db_name)

    # Register a customer
    customer_name = input("Enter customer name: ")
    phone_number = input("Enter customer phone number: ")
    address = input("Enter customer address: ")

    # Find customer using name and phone number
    customer_id = parking_system.find_customer(customer_name, phone_number)
    if not customer_id:
        logger.info("Customer not found, registering new customer.")
        customer_id = parking_system.register_customer(customer_name, phone_number, address)

    # Register a vehicle for the customer
    vehicle_number = input("Enter vehicle number: ")
    vehicle_type = input("Enter vehicle type (2-wheeler, 4-wheeler, 6-wheeler): ")

    vehicle_number = parking_system.register_vehicle(customer_id, vehicle_number, vehicle_type)

    if vehicle_number:
        # Add visit count and credit
        credit = parking_system.add_visit_and_credit(customer_id, vehicle_type)

        # Update parking duration if needed
        duration = int(input("Enter parking duration in days: "))
        parking_system.update_parking_duration(vehicle_number, duration)

        # Calculate total fee and apply discount if needed
        apply_discount = parking_system.apply_discount_on_next_visit(customer_id)
        total_fee = parking_system.calculate_total_fee(vehicle_number, apply_discount)

        # Log the final parking bill
        if total_fee is not None:
            logger.info(f"Final Parking Bill for Vehicle Number {vehicle_number}: Rs. {total_fee}")

        # Output the final fee and discount status
        if apply_discount:
            logger.info("Discount applied for the present visit.")
        else:
            logger.info("No discount for present visit.")
