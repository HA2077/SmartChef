from backend.user import save_users, load_users, User, Admin, Waiter, Chef
from backend.menuitem import MenuItem, save_menu_items, load_menu_items
from backend.order import Order, OrderItem, save_order, get_pending_orders, clear_all_orders
from backend.receipt import Receipt
import sys
import os

CURRENT_USER = None
MENU_ITEMS = []

def initialize_menu():
    global MENU_ITEMS
    MENU_ITEMS = load_menu_items()

def main_menu():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    initialize_menu()

    while True:
        print("\n" + "=" * 30)
        print("RESTAURANT MANAGEMENT SYSTEM CLI")
        print("=" * 30)
        
        if CURRENT_USER:
             print(f"Logged in as: {CURRENT_USER.get_username()} ({CURRENT_USER.get_role()})")
        else:
             print("Status: Not Logged In")
             
        print("-" * 30)
        print("1. POS System (Waiter)")
        print("2. Kitchen Display (Chef)")
        print("3. Manager Dashboard (Admin)")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            run_pos_cli()
        elif choice == '2':
            run_kitchen_cli()
        elif choice == '3':
            run_manager_cli()
        elif choice == '4':
            print("Exiting application. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

def login_user_flow(required_role=None):
    global CURRENT_USER
    if CURRENT_USER:
        if required_role and CURRENT_USER.get_role() != required_role:
            print(f"\n[ACCESS DENIED] You are logged in as '{CURRENT_USER.get_role()}', but '{required_role}' is required.")
            print("Please 'Logout' from your current menu first.")
            return False
        return True

    print("\n--- LOGIN REQUIRED ---")
    users = load_users() 
    
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    for user in users:
        if user.login(username, password):
            CURRENT_USER = user
            print(f"\nSUCCESS! Logged in as {CURRENT_USER.get_username()} ({CURRENT_USER.get_role().upper()}).")
            
            if required_role and CURRENT_USER.get_role() != required_role:
                print(f"ERROR: Access denied. This section requires {required_role} privileges.")
                CURRENT_USER = None # Reset if role doesn't match
                return False
            return True
            
    print("\nLOGIN FAILED. Invalid username or password.")
    CURRENT_USER = None
    return False

def display_menu():
    print("\n" + "=" * 60)
    print("AVAILABLE MENU ITEMS")
    print("=" * 60)
    
    categories = {}
    for item in MENU_ITEMS:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)
    
    for category in sorted(categories.keys()):
        print(f"\n{category.upper()}:")
        print("-" * 60)
        for item in categories[category]:
            print(f"  {item.id:5} | {item.name:20} | ${item.price:6.2f}")
    
    print("=" * 60)

def find_menu_item(item_id):
    for item in MENU_ITEMS:
        if item.id == item_id:
            return item
    return None

def add_item_to_order(order):
    display_menu()
    
    item_id = input("\nEnter Item ID to add (or 'back' to return): ").strip().upper()
    
    if item_id == 'BACK':
        return
    
    menu_item = find_menu_item(item_id)
    if not menu_item:
        print(f"ERROR: Item ID '{item_id}' not found.")
        return
    
    try:
        quantity = int(input(f"Enter quantity for {menu_item.name}: "))
        if quantity <= 0:
            print("ERROR: Quantity must be greater than 0.")
            return
        
        if order.add_item(menu_item.id, menu_item.name, menu_item.price, quantity):
            print(f"✓ Added {quantity}x {menu_item.name} @ ${menu_item.price:.2f} each")
        else:
            print("ERROR: Failed to add item to order.")
    except ValueError:
        print("ERROR: Invalid quantity. Please enter a number.")

def remove_item_from_order(order):
    if not order.items:
        print("ERROR: Order is empty. Nothing to remove.")
        return
    
    print("\nCURRENT ORDER ITEMS:")
    print("-" * 60)
    for i, item in enumerate(order.items, 1):
        print(f"  {i}. {item.name:20} | Qty: {item.quantity:2} | ${item.price:6.2f} each | Subtotal: ${item.subtotal:.2f}")
    
    try:
        item_index = int(input("\nEnter item number to remove (or 0 to cancel): "))
        
        if item_index == 0:
            return
        
        if 1 <= item_index <= len(order.items):
            item_to_remove = order.items[item_index - 1]
            remove_qty = input(f"Remove all {item_to_remove.quantity}x {item_to_remove.name}? (yes/no): ").strip().lower()
            
            if remove_qty == 'yes':
                if order.remove_item(item_to_remove.product_id):
                    print(f"✓ Removed {item_to_remove.name} from order.")
            else:
                qty_input = input("Enter quantity to remove: ")
                qty = int(qty_input)
                if qty > 0:
                    if order.remove_item(item_to_remove.product_id, qty):
                        print(f"✓ Removed {qty}x {item_to_remove.name} from order.")
        else:
            print("ERROR: Invalid item number.")
    except ValueError:
        print("ERROR: Invalid input. Please enter a number.")

def view_order_summary(order):
    if not order.items:
        print("\nOrder is empty.")
        return
    
    print("\n" + "=" * 60)
    print(f"ORDER SUMMARY - {order.order_id}")
    print("=" * 60)
    print(f"Status: {order.status}")
    print("-" * 60)
    
    for item in order.items:
        print(f"{item.name:20} | Qty: {item.quantity:2} | ${item.price:6.2f} x {item.quantity} | ${item.subtotal:8.2f}")
    
    print("-" * 60)
    print(f"{'TOTAL':20} | {' ' * 22} | ${order.get_total():8.2f}")
    print("=" * 60)

def run_pos_cli():
    global CURRENT_USER
    if not login_user_flow(required_role="waiter"):
        return

    print("\n--- POS System ---")
    print(f"Welcome, {CURRENT_USER.get_username()}!")
    
    table_id = input("Enter Table ID/Customer ID for new order: ").strip()
    if not table_id:
        print("ERROR: Table ID cannot be empty.")
        return
    
    current_order = Order(customer_id=table_id)
    
    while True:
        print(f"\n[Order: {current_order.order_id} | Table: {table_id} | Status: {current_order.status}]")
        print("\nPOS MENU:")
        print("1. Add Item")
        print("2. Remove Item")
        print("3. View Order")
        print("4. Submit Order to Kitchen")
        print("5. Cancel Order")
        print("6. Back to Main Menu (Keep Logged In)")
        print("7. Logout")
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            add_item_to_order(current_order)
        elif choice == '2':
            remove_item_from_order(current_order)
        elif choice == '3':
            view_order_summary(current_order)
        elif choice == '4':
            if not current_order.items:
                print("ERROR: Cannot submit empty order.")
            else:
                current_order.update_status(Order.PENDING)
                save_order(current_order)
                print("\n" + "="*40)
                print(f"✓ Order {current_order.order_id} sent to KITCHEN successfully!")
                print("="*40)
                # Optionally clear current order or break to start new one
                # For now, let's keep them in the menu to start a new one or logout
                current_order = Order(customer_id=table_id) # Reset for next order
        elif choice == '5':
            confirm = input("Are you sure you want to cancel this order? (yes/no): ").strip().lower()
            if confirm == 'yes':
                current_order.update_status(Order.CANCELLED)
                print("✓ Order cancelled.")
                break
        elif choice == '6':
            print("Returning to main menu...")
            break
        elif choice == '7':
            print(f"Logging out {CURRENT_USER.get_username()}...")
            CURRENT_USER = None
            break
        else:
            print("Invalid choice. Please try again.")

def run_kitchen_cli():
    global CURRENT_USER
    if not login_user_flow(required_role="chef"):
        return
    
    print(f"\n--- Kitchen Display System (Chef: {CURRENT_USER.get_username()}) ---")
    
    while True:
        pending_orders = get_pending_orders()
        
        print("\n" + "="*60)
        print(f"PENDING ORDERS QUEUE ({len(pending_orders)})")
        print("="*60)
        
        if not pending_orders:
            print("No pending orders. Waiting for waiters...")
        else:
            for i, order in enumerate(pending_orders, 1):
                items_str = ", ".join([f"{item.quantity}x {item.name}" for item in order.items])
                print(f"{i}. [#{order.order_id}] Table: {order.customer_id}")
                print(f"   Time: {order.created_at.strftime('%H:%M')} | Items: {items_str}")
                print("-" * 60)

        print("\nOPTIONS:")
        print(" [R] Refresh List")
        print(" [Number] Complete Order (e.g., 1)")
        print(" [B] Back to Main Menu (Keep Logged In)")
        print(" [L] Logout")
        
        choice = input("Action: ").strip().upper()
        
        if choice == 'B':
            break
        elif choice == 'L':
            print(f"Logging out {CURRENT_USER.get_username()}...")
            CURRENT_USER = None
            break
        elif choice == 'R':
            continue
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(pending_orders):
                order_to_complete = pending_orders[idx]
                
                order_to_complete.update_status(Order.COMPLETED)
                save_order(order_to_complete)
                
                receipt = Receipt(order_to_complete)
                file_path = receipt.save_to_file()
                
                print(f"\n>>> Order {order_to_complete.order_id} marked COMPLETED! <<<")
                print(f">>> Receipt generated automatically at: {file_path}")
                print("-" * 40)
                print(receipt.generate_simple_receipt())
                print("-" * 40)
                input("\nPress Enter to continue...")
            else:
                print("ERROR: Invalid order number.")
        else:
            print("Invalid option.")

def view_users():
    users = load_users()
    print("\n" + "=" * 40)
    print("SYSTEM USERS")
    print("=" * 40)
    if not users:
        print("No users found.")
        return
    
    for user in users:
        print(f"  - {user.get_username():<15} | Role: {user.get_role().upper()}")
    print("=" * 40)

def add_user():
    users = load_users()
    print("\n--- ADD NEW USER ---")
    
    username = input("Enter new username: ").strip()
    if not username:
        print("ERROR: Username cannot be empty.")
        return
        
    for user in users:
        if user.get_username() == username:
            print(f"ERROR: User '{username}' already exists.")
            return

    password = input("Enter password: ").strip()
    if not password:
        print("ERROR: Password cannot be empty.")
        return
        
    role = input("Enter role (admin, waiter, chef): ").strip().lower()
    if role not in ["admin", "waiter", "chef"]:
        print("ERROR: Invalid role. Must be 'admin', 'waiter', or 'chef'.")
        return

    if role == "admin":
        new_user = Admin(username, password)
    elif role == "waiter":
        new_user = Waiter(username, password)
    elif role == "chef":
        new_user = Chef(username, password)
    else:
        new_user = User(username, password, role)
    
    users.append(new_user)
    save_users(users)
    print(f"✓ Successfully added new user: {username} ({role.upper()})")

def add_menu_item_manager():
    print("\n--- ADD NEW MENU ITEM ---")
    
    item_id = input("Enter Item ID (e.g., F1): ").strip().upper()
    if find_menu_item(item_id):
        print("ERROR: Item ID already exists.")
        return
    
    name = input("Enter Item Name: ").strip()
    category = input("Enter Category (e.g., Food, Drinks): ").strip()
    
    try:
        price = float(input("Enter Price: "))
    except ValueError:
        print("ERROR: Invalid price.")
        return
        
    new_item = MenuItem(item_id, name, category, price)
    MENU_ITEMS.append(new_item)
    if save_menu_items(MENU_ITEMS):
        print(f"✓ Added {name} to menu.")
    else:
        print("ERROR: Could not save menu.")

def remove_menu_item_manager():
    print("\n--- REMOVE MENU ITEM ---")
    display_menu()
    
    item_id = input("\nEnter ID of item to remove: ").strip().upper()
    
    for i, item in enumerate(MENU_ITEMS):
        if item.id == item_id:
            confirm = input(f"Are you sure you want to delete {item.name}? (yes/no): ").lower()
            if confirm == 'yes':
                MENU_ITEMS.pop(i)
                save_menu_items(MENU_ITEMS)
                print(f"✓ Removed item {item_id}.")
                return
            else:
                print("Deletion cancelled.")
                return
    
    print("ERROR: Item ID not found.")

def run_manager_cli():
    global CURRENT_USER
    if not login_user_flow(required_role="admin"):
        return
        
    while True:
        print("\n--- Manager Dashboard ---")
        print(f"Welcome, {CURRENT_USER.get_username()}!")
        print("-" * 30)
        print("1. View All Users")
        print("2. Add New User")
        print("3. Add Menu Item")
        print("4. Remove Menu Item")
        print("5. Back to Main Menu (Keep Logged In)")
        print("6. Logout")
        print("-" * 30)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            view_users()
        elif choice == '2':
            add_user()
        elif choice == '3':
            add_menu_item_manager()
        elif choice == '4':
            remove_menu_item_manager()
        elif choice == '5':
            print("Returning to main menu...")
            break
        elif choice == '6':
            print(f"Logging out {CURRENT_USER.get_username()}...")
            CURRENT_USER = None
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()