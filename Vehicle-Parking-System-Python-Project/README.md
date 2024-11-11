# Vehicle Parking System

This project implements a simple Vehicle Parking System that interacts with a MySQL database to register customers, vehicles, and manage parking information such as parking duration, fees, and discounts. The system supports 2-wheeler, 4-wheeler, and 6-wheeler vehicles and applies credits and discounts for frequent visitors.

## Features

- **Customer Registration:** Allows for registering new customers with their name, phone number, and address.
- **Vehicle Registration:** Supports the registration of vehicles with details such as vehicle number, type (2-wheeler, 4-wheeler, or 6-wheeler), and parking duration.
- **Parking Fee Calculation:** Calculates the parking fee based on vehicle type and duration of stay.
- **Discounts & Credits:** Provides a discount on the next visit based on the number of visits and applies credit to customers after their first visit.
- **Database Support:** Uses a MySQL database to store customer and vehicle data.
- **Logging:** Utilizes the `loguru` logger for logging important system events.

## Prerequisites

Before running the system, ensure that you have the following installed:

- Python 3.x
- MySQL server
- `pymysql` and `loguru` libraries

You can install the required Python libraries using `pip`:

```bash
pip install pymysql loguru
