# 🧑‍🍳 SmartChef Restaurant System

[![Python](https://img.shields.io/badge/Python-3.12.3-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Tkinter-brightgreen?style=flat-square&logo=tcl)](https://docs.python.org/3/library/tkinter.html)
[![Status](https://img.shields.io/badge/Status-Ready%20to%20Use-success?style=flat-square)]()

A comprehensive restaurant management solution developed in Python for our Object-Oriented Programming (OOP) course. SmartChef provides distinct dashboards for managerial oversight, order fulfillment, and kitchen preparation, ensuring a smooth operational flow.

---

## ✨ Core Features

SmartChef is designed to cover the three main pillars of a modern restaurant:

### 📊 Admin Dashboard (Manager)
* **Live Analytics:** Track total revenue, pending orders, and completed orders in real-time.
* **Queue Monitoring:** View the live kitchen queue and overall order history.
* **User & Menu Management:** Add/remove users (Admin, Waiter, Chef) and manage the entire menu item catalog.

### 🍽️ Point of Sale (POS / Waiter)
* **Intuitive Ordering:** Easily add or remove items from the menu categories.
* **Order Control:** Assign orders to tables and submit them directly to the Kitchen Display.
* **Automatic Totals:** Calculates subtotal, tax (8%), and grand total automatically.

### 👨‍🍳 Kitchen Display System (KDS / Chef)
* **Ticket View:** Displays active orders with customer/table ID and item lists.
* **Status Workflow:** Chefs can transition orders from PENDING ➡️ PROCESSING ➡️ COMPLETED with a single click.
* **Receipts:** Automatically generates a detailed receipt file upon marking an order as COMPLETED.

---

## 💻 Tech Stack

* **Language:** Python 3.12.3
* **GUI Framework:** Tkinter (No external image libraries used for better Linux/Windows binary compatibility)
* **Bundling:** PyInstaller (for cross-platform executables)

## ⬇️ Installation

### Prerequisites
* Python 3.12.3

### Executables (Recommended)
Download the pre-built binaries from the [[Releases](https://github.com/HA2077/SmartChef/releases)] page:
* **Windows:** `SmartChef.rar`
* **Linux (Debian/Ubuntu):** `SmartChef.tar.xz`

### From Source
1.  Clone the repository:
    ```bash
    git clone https://github.com/HA2077/SmartChef
    cd SmartChef
    ```
2.  Run the main application:
    ```bash
    python3 main.py
    ```

## 🔑 Default Credentials (For Testing)

| Role | Username | Password |
| :--- | :--- | :--- |
| **Manager (Admin)** | `hassan` | `HA` |
| **Waiter** | `zoz` | `zoz` |
| **Chef** | `Abr7` | `1234` |

---

## 🏗️ Object-Oriented Design (The Four Pillars)

This project is structured around the four fundamental principles of Object-Oriented Programming, as demonstrated in our `backend` classes:

* **1. Encapsulation:**
    * Data (attributes like `username`, `password`) and the methods operating on that data are bundled together within classes like `User` and `Order`.
    * The `User` class enforces access control by using private attributes (`self.__username`, `self.__password`) which are only accessible through designated public methods (`get_username()`, `login()`).

* **2. Abstraction:**
    * Complex internal logic is hidden from the main application flow. For example, the `Order` class provides simple methods like `add_item()` or `get_total()`, concealing the intricate details of iterating over item lists and performing sum calculations.
    * The `Receipt` class exposes methods like `generate_detailed_receipt()`, hiding the formatting and calculation logic.

* **3. Inheritance:**
    * The `Admin`, `Waiter`, and `Chef` classes are derived from the base `User` class.
    * They inherit common properties (username, password, login function) and specialize their behavior by setting their unique `role`.

* **4. Polymorphism:**
    * Different user types (`Admin`, `Waiter`, `Chef`) are handled uniformly by the `LoginWindow` logic when verifying roles, checking the type of the abstract `User` object.
    * Any object that inherits from `MenuItem` or is contained within the `Order` items list can be processed uniformly to calculate the order's total value.

---

## 📈 Future Improvements

We have identified several key areas for future development to enhance the stability, scalability, and performance of SmartChef:

* **Proper Backend/Database:** Migrate from local JSON file storage to a robust relational database (e.g., PostgreSQL, MySQL) or a proper NoSQL solution for improved data integrity and concurrent user access.
* **C++ Integration for Queue (DSA):** Implement the core order processing queue using C++ for maximum performance, leveraging Data Structures and Algorithms (DSA) principles to handle order flow efficiently under high load.
* **Network Capabilities:** Implement client-server architecture so POS, Kitchen, and Admin dashboards can operate on separate devices.
* **Advanced Analytics:** Add features like trend analysis, labor cost reporting, and inventory management.
* **Modern GUI Framework:** Transition from Tkinter to a more modern GUI library (like PyQt, Kivy, or CustomTkinter) to improve the user interface aesthetic and modern look.

---

## 🙏 Acknowledgment

A massive thank you to my incredible teammates for their hard work, dedication, and collaboration on this project:

* **Abdelrahman**
* **Abdullah**
* **Amr**
* **Salem**
* **Ziad**

We built this application from the ground up, and I couldn't have asked for a better team!

---
**Made with ❤️ for Coding**