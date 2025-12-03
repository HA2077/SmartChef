from backend.user import load_users, User, Admin, Waiter, Chef
from backend.menuitem import MenuItem
from backend.order import Order, OrderItem
from backend.receipt import Receipt
import sys

CURRENT_USER = None

MENU_ITEMS = [
    MenuItem("A1", "Burger", "Food", 15.00),
    MenuItem("A2", "Pizza", "Food", 21.05),
    MenuItem("A3", "Pasta", "Food", 12.00),
    MenuItem("A4", "Koshary", "Food", 13.69),
    MenuItem("A5", "Shawrama", "Food", 14.15),
    MenuItem("B1", "Soda", "Drinks", 3.00),
    MenuItem("B2", "Coffee", "Drinks", 4.50),
    MenuItem("B3", "Chocolate Milk", "Drinks", 6.67),
    MenuItem("D1", "Cake", "Dessert", 7.00),
    MenuItem("D2", "Brownies", "Dessert", 10.44),
    MenuItem("D3", "Ice Cream", "Dessert", 5.50)
]

def main_menu():
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
    global CURRENT_USER
    
    users = load_users() 
    
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    for user in users:
        if user.login(username, password):
            CURRENT_USER = user
            print(f"\nSUCCESS! Logged in as {CURRENT_USER.get_username()} ({CURRENT_USER.get_role().upper()}).")
            return
            
    print("\nLOGIN FAILED. Invalid username or password.")
    CURRENT_USER = None

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
    if not CURRENT_USER or CURRENT_USER.get_role() != "waiter":
        print("\nACCESS DENIED. You must log in as a WAITER to use the POS system.")
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
        print("6. Back to Main Menu")
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            add_item_to_order(current_order)
        
        elif choice == '2':
            remove_item_from_order(current_order)
        
        elif choice == '3':
            view_order_summary(current_order)
        
        elif choice == '4':
            if not current_order.items:
                print("ERROR: Cannot submit empty order.")
            elif current_order.update_status(Order.PENDING):
                view_order_summary(current_order)
                receipt = Receipt(current_order)
                print("\n" + receipt.generate_simple_receipt())
                print("\n✓ Order submitted to kitchen!")
                break
            else:
                print("ERROR: Failed to submit order.")
        
        elif choice == '5':
            confirm = input("Are you sure you want to cancel this order? (yes/no): ").strip().lower()
            if confirm == 'yes':
                current_order.update_status(Order.CANCELLED)
                print("✓ Order cancelled.")
                break
        
        elif choice == '6':
            print("Returning to main menu...")
            break
        
        else:
            print("Invalid choice. Please try again.")

def run_kitchen_cli():
    global CURRENT_USER
    if not CURRENT_USER or CURRENT_USER.get_role() != "chef":
        print("\nACCESS DENIED. You must log in as a CHEF to view the kitchen display.")
        return
    
    print("\n--- Kitchen Display System ---")
    print(f"Welcome, {CURRENT_USER.get_username()}!")
    print("Chef view: Here you would see a list of PENDING orders.")
    print("e.g. Order ORD-XXXX is PENDING.")

def run_manager_cli():
    global CURRENT_USER
    if not CURRENT_USER or CURRENT_USER.get_role() != "admin":
        print("\nACCESS DENIED. You must log in as an ADMIN (Manager) to view the dashboard.")
        return
        
    print("\n--- Manager Dashboard ---")
    print(f"Welcome, {CURRENT_USER.get_username()}!")
    print("Manager view: Here you would see revenue stats and manage users.")

if __name__ == "__main__":
    main_menu()