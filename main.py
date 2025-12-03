from backend.user import load_users, User, Admin, Waiter, Chef
from backend.menuitem import MenuItem
from backend.order import Order, OrderItem
from backend.receipt import Receipt
import sys

# Global state for simplicity in CLI
CURRENT_USER = None

def main_menu():
    """Displays the main menu and handles user selection."""
    while True:
        print("\n" + "=" * 30)
        print("RESTAURANT MANAGEMENT SYSTEM CLI")
        print("=" * 30)
        print("1. Login")
        print("2. POS System (Requires Waiter Login)")
        print("3. Kitchen Display (Requires Chef Login)")
        print("4. Manager Dashboard (Requires Admin Login)")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            login_user()
        elif choice == '2':
            run_pos_cli()
        elif choice == '3':
            run_kitchen_cli()
        elif choice == '4':
            run_manager_cli()
        elif choice == '5':
            print("Exiting application. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

def login_user():
    """Handles the user login process."""
    global CURRENT_USER
    
    users = load_users()  # Load users from data/users.json
    
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    for user in users:
        if user.login(username, password):
            CURRENT_USER = user
            print(f"\nSUCCESS! Logged in as {CURRENT_USER.get_username()} ({CURRENT_USER.get_role().upper()}).")
            return
            
    print("\nLOGIN FAILED. Invalid username or password.")
    CURRENT_USER = None

def run_pos_cli():
    """Simulates the POS system interface."""
    global CURRENT_USER
    if not CURRENT_USER or CURRENT_USER.get_role() != "waiter":
        print("\nACCESS DENIED. You must log in as a WAITER to use the POS system.")
        return

    print("\n--- POS System ---")
    print(f"Welcome, {CURRENT_USER.get_username()}!")
    
    # --- Example POS Workflow ---
    table_id = input("Enter Table ID/Customer ID for new order: ")
    current_order = Order(customer_id=table_id)
    
    # Dummy Menu Items for testing (replace with actual loading later)
    item_a = MenuItem("A1", "Burger", "Food", 15.00)
    item_b = MenuItem("B1", "Soda", "Drinks", 3.00)

    print("\nAdding test items to order:")
    current_order.add_item(item_a.id, item_a.name, item_a.price, 2)
    current_order.add_item(item_b.id, item_b.name, item_b.price, 1)
    
    print(f"Current Order Total: ${current_order.get_total():.2f}")
    
    current_order.update_status(Order.PENDING)
    print(f"Order {current_order.order_id} sent to kitchen. Status: {current_order.status}")
    
    # Generate Receipt Example
    receipt = Receipt(current_order)
    print("\n" + "=" * 40)
    print("Example Simple Receipt:")
    print(receipt.generate_simple_receipt())
    print("=" * 40)
    

def run_kitchen_cli():
    """Simulates the Kitchen Display interface."""
    global CURRENT_USER
    if not CURRENT_USER or CURRENT_USER.get_role() != "chef":
        print("\nACCESS DENIED. You must log in as a CHEF to view the kitchen display.")
        return
    
    print("\n--- Kitchen Display System ---")
    print(f"Welcome, {CURRENT_USER.get_username()}!")
    print("Chef view: Here you would see a list of PENDING orders.")
    print("e.g. Order ORD-XXXX is PENDING.")
    # In the full application, you would load all PENDING orders from orders.json and display them.

def run_manager_cli():
    """Simulates the Manager Dashboard interface."""
    global CURRENT_USER
    if not CURRENT_USER or CURRENT_USER.get_role() != "admin":
        print("\nACCESS DENIED. You must log in as an ADMIN (Manager) to view the dashboard.")
        return
        
    print("\n--- Manager Dashboard ---")
    print(f"Welcome, {CURRENT_USER.get_username()}!")
    print("Manager view: Here you would see revenue stats and manage users.")
    # In the full application, you would display revenue statistics and controls for managing users.

if __name__ == "__main__":
    main_menu()