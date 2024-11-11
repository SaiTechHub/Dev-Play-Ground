# MyHotel - A Python Hotel Management System

`hotel_app - MyHotel` is a simple hotel management system built in Python, utilizing MySQL for database storage. This system allows you to manage customer information, take orders for meals, apply credits, and gather feedback.

## Features

- **Customer Management**: Create and store customer information including name, address, phone number, and credits.
- **Order Management**: Place orders for breakfast or lunch, calculate item prices, apply credits, and generate the bill.
- **Feedback Collection**: Collect and store customer feedback after their visit.
- **Credit System**: Customers can accumulate credits for future orders, which can be used to reduce the total bill.
- **Database Integration**: Uses MySQL to store customer data, orders, and feedback.

## Requirements

- Python 3.x
- MySQL database server
- `pymysql` for MySQL integration
- `loguru` for logging

### Install Dependencies

You can install the required Python libraries with the following command:

```bash
pip install pymysql loguru
