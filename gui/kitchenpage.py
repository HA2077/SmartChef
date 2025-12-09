import tkinter as tk
import time 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.order import load_orders, Order as OrderClass, save_order
from backend.receipt import Receipt
BG_COLOR = "#2B0505"
CARD_COLOR = "#450A0A"
TEXT_WHITE = "#FFFFFF"

# Status Colors
STATUS_PENDING = "#FFC107"  # Yellow
STATUS_PREP = "#0D6EFD"     # Blue
STATUS_READY = "#198754"    # Green

class KitchenDashboard(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("SmartChef - Kitchen Display")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)
        self.order_widgets = {} # Stores references to the frames for easy updating
        self.last_load_time = 0
        # Header
        header = tk.Frame(self, bg=BG_COLOR, height=60)
        header.pack(fill="x", padx=20, pady=10)
        tk.Label(header, text="Kitchen Display - Active Orders", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg="#999").pack(anchor="w")

        # Scrollable Area (Simplified as a grid frame for demo)
        self.grid_frame = tk.Frame(self, bg=BG_COLOR)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)
        for i in range(4): # Assuming 4 columns max
            self.grid_frame.columnconfigure(i, weight=1)
        
        self.load_and_display_orders()
        self.start_refresh_timer()

    def start_refresh_timer(self):
        """Sets up a timer to check for new orders every 1000ms (1 second)."""
        # 1000ms = 1 second
        self.after(1000, self.load_and_display_orders) 

    def load_and_display_orders(self):
        """Loads orders and updates the display."""
        orders = [o for o in load_orders() if o.status in [OrderClass.PENDING, OrderClass.PROCESSING]]
        
        current_ids = set(self.order_widgets.keys())
        active_ids = set(o.order_id for o in orders)
        
        # 1. Remove widgets for completed/cancelled orders
        for order_id in current_ids - active_ids:
            if order_id in self.order_widgets:
                self.order_widgets[order_id].destroy()
                del self.order_widgets[order_id]

        # 2. Add/Update widgets for active orders
        for i, order in enumerate(orders):
            row, col = divmod(i, 4) # Arrange orders in 4 columns
            
            # Check for new order to apply visual highlight
            is_new = (order.order_id not in current_ids) and (time.time() - self.last_load_time < 5) # Highlight for 5 seconds
            
            if order.order_id not in self.order_widgets:
                # Create a new ticket if it doesn't exist
                self.create_ticket(row, col, order, is_new)
            else:
                # Ensure existing ticket is updated and positioned correctly
                self.update_ticket(self.order_widgets[order.order_id], row, col, order)
                
        self.last_load_time = time.time()
        self.start_refresh_timer() # Loop the timer

    def update_ticket(self, container, row, col, order):
        """Updates the position and status of an existing ticket."""
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        # Update status colors and text here if needed (not fully implemented in base structure, but placement is fixed)


    def change_order_status(self, order_id, new_status):
        """Changes order status, saves to JSON, and generates receipt if completed."""
        orders = load_orders()
        for i, order in enumerate(orders):
            if order.order_id == order_id:
                if order.update_status(new_status):
                    
                    # --- START ADDED LOGIC FOR RECEIPT GENERATION ---
                    if new_status == OrderClass.COMPLETED:
                        try:
                            # 1. Instantiate the Receipt object
                            receipt = Receipt(order)
                            # 2. Save the receipt to a file (as defined in receipt.py)
                            filename = receipt.save_to_file()
                            print(f"Receipt generated for order {order_id}: {filename}")
                        except ValueError as e:
                            print(f"Error generating receipt for order {order_id}: {e}")
                    # --- END ADDED LOGIC FOR RECEIPT GENERATION ---
                    
                    save_order(order)
                    # Force immediate refresh
                    self.load_and_display_orders()
                    return
        print(f"Error: Could not find or update order {order_id}")

    # --- Modified create_ticket function to use real data ---
    def create_ticket(self, row, col, order: OrderClass, is_new: bool = False):
        table_name = order.customer_id
        
        # Border Frame (Simulates the glow)
        border_color = "white"
        if order.status == OrderClass.PENDING: border_color = STATUS_PENDING
        elif order.status == OrderClass.PROCESSING: border_color = STATUS_PREP
        elif order.status == OrderClass.COMPLETED: border_color = STATUS_READY
        
        # Highlight new orders briefly
        if is_new:
            border_color = "#FF00FF" # Magenta highlight for new orders

        container = tk.Frame(self.grid_frame, bg=border_color, padx=2, pady=2)
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        self.order_widgets[order.order_id] = container

        # Inner Card
        card = tk.Frame(container, bg=CARD_COLOR, width=280, height=220)
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)

        # Header
        tk.Label(card, text=f"Order #{order.order_id[-4:]}", font=("Segoe UI", 9), bg=CARD_COLOR, fg="#CCC").place(x=15, y=10)
        
        # Action button to progress order
        next_status = OrderClass.PROCESSING if order.status == OrderClass.PENDING else OrderClass.COMPLETED
        next_text = "START PREP" if order.status == OrderClass.PENDING else "READY"
        
        btn_cmd = lambda oid=order.order_id, ns=next_status: self.change_order_status(oid, ns)
        
        btn_color = STATUS_PREP if order.status == OrderClass.PENDING else STATUS_READY
        
        action_btn = tk.Button(card, text=next_text, font=("Segoe UI", 10, "bold"), 
                               bg=btn_color, fg="white", relief="flat", command=btn_cmd)
        action_btn.place(x=180, y=10, width=90, height=25)


        # Table Name
        tk.Label(card, text=table_name, font=("Segoe UI", 24, "bold"), bg=CARD_COLOR, fg="white").place(x=15, y=30)

        # Items (limit to 4 lines)
        item_list = [f"{item.quantity}x {item.name}" for item in order.items]
        items_text = "\n".join(item_list[:4]) + ("..." if len(item_list) > 4 else "")
        tk.Label(card, text=items_text, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#EEE", justify="left").place(x=15, y=80)

        # Timer (Currently just the creation time)
        time_val = order.created_at.strftime('%H:%M')
        tk.Label(card, text=time_val, font=("Segoe UI", 18, "bold"), bg=CARD_COLOR, fg="white").place(x=200, y=85)

        # Status Pill
        btn_bg = border_color
        status_lbl = tk.Label(card, text=order.status, font=("Segoe UI", 10, "bold"), 
                              bg=btn_bg, fg="black" if order.status=="Pending" else "white", width=15, pady=5)
        status_lbl.place(x=80, y=170)
        
        container.update_idletasks() # Ensure dimensions are set

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = KitchenDashboard()
    root.mainloop()