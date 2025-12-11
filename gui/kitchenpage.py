import tkinter as tk
import time 
import sys
import os
import json
from PIL import Image, ImageTk 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.order import load_orders, Order as OrderClass, save_order
from backend.receipt import Receipt

BG_COLOR = "#2B0505"
CARD_COLOR = "#450A0A"
TEXT_WHITE = "#FFFFFF"

# Status Colors
STATUS_PENDING = "#FFC107"  # Yellow
STATUS_PREP = "#0D6EFD"     # Blue (Processing)
STATUS_READY = "#198754"    # Green (Ready to Complete)

class KitchenDashboard(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("SmartChef - Kitchen Display")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)
        
        # --- Background Image Setup ---
        self.bg_image_original = None
        self.bg_photo = None
        self.bg_label = tk.Label(self, bg=BG_COLOR)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.load_background()
        
        self.order_widgets = {}   # Maps order_id -> container_frame
        self.last_statuses = {}   # Maps order_id -> status (Prevents flickering)
        
        # Header 
        self.header = tk.Frame(self, bg=BG_COLOR, height=60)
        self.header.pack(fill="x", padx=20, pady=10)
        tk.Label(self.header, text="Kitchen Display - Active Orders", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg="#FFFFFF").pack(anchor="w")

        # Grid Frame for Tickets
        self.grid_frame = tk.Frame(self, bg=BG_COLOR)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        for i in range(4):
            self.grid_frame.columnconfigure(i, weight=1)
        
        self.load_and_display_orders()
        self.start_refresh_timer()
        
        self.bind("<Configure>", self.resize_background)

    def load_background(self):
        bg_path = "assets/BG.jpg"
        if os.path.exists(bg_path):
            try:
                self.bg_image_original = Image.open(bg_path)
                self.resize_background(None)
            except Exception as e:
                print(f"Error loading background: {e}")

    def resize_background(self, event):
        if self.bg_image_original:
            w = self.winfo_width()
            h = self.winfo_height()
            if w > 0 and h > 0:
                resized = self.bg_image_original.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(resized)
                self.bg_label.config(image=self.bg_photo)
                self.bg_label.lower()

    def start_refresh_timer(self):
        self.after(1000, self.load_and_display_orders) 

    def load_and_display_orders(self):
        # 1. Load Data (Only show Pending or Processing)
        # Completed orders are now in the JSON, but we filter them out here so they disappear from the UI.
        orders = [o for o in load_orders() if o.status in [OrderClass.PENDING, OrderClass.PROCESSING]]
        active_ids = set(o.order_id for o in orders)
        
        # 2. CLEANUP: Remove widgets for orders that are gone (Completed or not in list)
        for order_id in list(self.order_widgets.keys()):
            if order_id not in active_ids:
                self.order_widgets[order_id].destroy()
                del self.order_widgets[order_id]
                if order_id in self.last_statuses:
                    del self.last_statuses[order_id]

        # 3. UPDATE/CREATE: Render active orders
        for i, order in enumerate(orders):
            row, col = divmod(i, 4)
            current_status = order.status
            prev_status = self.last_statuses.get(order.order_id)
            
            if order.order_id not in self.order_widgets:
                # NEW ORDER
                self.create_ticket_frame(row, col, order)
                self.last_statuses[order.order_id] = current_status
            
            elif current_status != prev_status:
                # STATUS CHANGED (Re-render)
                container = self.order_widgets[order.order_id]
                self.render_ticket_content(container, order, is_new=False)
                self.last_statuses[order.order_id] = current_status
                container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            else:
                # NO CHANGE (Just Grid)
                container = self.order_widgets[order.order_id]
                container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        self.start_refresh_timer()

    def change_order_status(self, order_id, new_status):
        orders = load_orders()
        for i, order in enumerate(orders):
            if order.order_id == order_id:
                if order.update_status(new_status):
                    
                    if new_status == OrderClass.COMPLETED:
                        # 1. Generate Receipt
                        try:
                            receipt = Receipt(order)
                            filename = receipt.save_to_file()
                            print(f"Receipt generated: {filename}")
                        except ValueError as e:
                            print(f"Error generating receipt: {e}")
                        
                        # 2. SAVE status as COMPLETED (Do NOT delete from JSON)
                        # This keeps the order in the file for records/admin view
                        save_order(order)
                    else:
                        # Update status (e.g. to PROCESSING) and save
                        save_order(order)
                    
                    # Force immediate refresh
                    self.load_and_display_orders()
                    return
        print(f"Error: Could not find order {order_id}")

    def create_ticket_frame(self, row, col, order, is_new=False):
        container = tk.Frame(self.grid_frame, padx=2, pady=2)
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        self.order_widgets[order.order_id] = container
        self.render_ticket_content(container, order, is_new)

    def render_ticket_content(self, container, order: OrderClass, is_new: bool):
        for widget in container.winfo_children():
            widget.destroy()

        border_color = "white"
        if order.status == OrderClass.PENDING: border_color = STATUS_PENDING
        elif order.status == OrderClass.PROCESSING: border_color = STATUS_PREP
        elif order.status == OrderClass.COMPLETED: border_color = STATUS_READY
        
        if is_new:
            border_color = "#FF00FF"
            
        container.configure(bg=border_color)

        card = tk.Frame(container, bg=CARD_COLOR, width=280, height=220)
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)

        tk.Label(card, text=f"Order #{order.order_id[-4:]}", font=("Segoe UI", 9), bg=CARD_COLOR, fg="#CCC").place(x=15, y=10)

        # Button Logic
        if order.status == OrderClass.PENDING:
            next_status = OrderClass.PROCESSING
            next_text = "START PREP"
            btn_bg = STATUS_PREP 
        else:
            next_status = OrderClass.COMPLETED
            next_text = "COMPLETE"
            btn_bg = STATUS_READY 
        
        btn_cmd = lambda oid=order.order_id, ns=next_status: self.change_order_status(oid, ns)
        
        action_btn = tk.Button(card, text=next_text, font=("Segoe UI", 10, "bold"), 
                               bg=btn_bg, fg="white", relief="flat", command=btn_cmd)
        action_btn.place(x=180, y=10, width=90, height=25)

        tk.Label(card, text=order.customer_id, font=("Segoe UI", 24, "bold"), bg=CARD_COLOR, fg="white").place(x=15, y=30)

        item_list = [f"{item.quantity}x {item.name}" for item in order.items]
        items_text = "\n".join(item_list[:4]) + ("..." if len(item_list) > 4 else "")
        tk.Label(card, text=items_text, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#EEE", justify="left").place(x=15, y=80)

        time_val = order.created_at.strftime('%H:%M')
        tk.Label(card, text=time_val, font=("Segoe UI", 18, "bold"), bg=CARD_COLOR, fg="white").place(x=200, y=85)

        status_lbl = tk.Label(card, text=order.status, font=("Segoe UI", 10, "bold"), 
                              bg=border_color, fg="black" if order.status=="Pending" else "white", width=15, pady=5)
        status_lbl.place(x=80, y=170)
        
        container.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = KitchenDashboard()
    root.mainloop()