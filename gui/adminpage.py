import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

# make backend importable when running from gui folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.order import load_orders, Order as OrderClass

# --- COLORS FROM YOUR SCREENSHOT ---
BG_COLOR = "#2B0505"       # Very dark red (Background)
SIDEBAR_COLOR = "#450A0A"  # Slightly lighter sidebar
CARD_COLOR = "#6A0D0D"     # The "Card" red
TEXT_WHITE = "#FFFFFF"
ACCENT_GOLD = "#FFD700"
ACCENT_GREEN = "#28a745"

class AdminDashboard(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("SmartChef - Admin Dashboard")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)

        # Sidebar
        self.sidebar = tk.Frame(self, bg=SIDEBAR_COLOR, width=80)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.build_sidebar_icons()

        # Main Content
        self.main_area = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Prepare storage for stat label references
        self.stat_labels = {}

        self.build_stats_row()
        self.build_queue_section()
        self.build_table_section()

        # Start auto-refresh (queues + stats)
        self.refresh_queues()

    def build_sidebar_icons(self):
        # Fake Icons using text
        icons = ["📋", "📊", "👥"]

        # Logo placeholder
        tk.Label(self.sidebar, text="👨‍🍳", font=("Segoe UI", 30), bg=SIDEBAR_COLOR, fg="white").pack(pady=20)

        for icon in icons:
            btn = tk.Label(self.sidebar, text=icon, font=("Segoe UI", 20),
                           bg=SIDEBAR_COLOR, fg="#AA5555", cursor="hand2")
            btn.pack(pady=15, fill="x")
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#AA5555"))

            # Click events for different icons
            if icon == "👥":
                btn.bind("<Button-1>", self.open_users_management)
            elif icon == "📋":
                btn.bind("<Button-1>", self.open_menu_management)
            elif icon == "📊":
                btn.bind("<Button-1>", self.open_reports_analytics)

        # Logout at bottom
        tk.Label(self.sidebar, text="🚪", font=("Segoe UI", 20),
                 bg=SIDEBAR_COLOR, fg="#AA5555", cursor="hand2").pack(side="bottom", pady=20)

    # ----------------------
    # Live Stats (dynamic)
    # ----------------------
    def build_stats_row(self):
        stats_frame = tk.Frame(self.main_area, bg=BG_COLOR)
        stats_frame.pack(fill="x", pady=(0, 10))

        # store references to value label widgets so we can update them
        self.stat_labels['revenue'] = self.create_card(stats_frame, "REVENUE", "$0.00", "💲")
        self.stat_labels['pending'] = self.create_card(stats_frame, "PENDING", "0 ORDERS", "🕒")
        self.stat_labels['completed'] = self.create_card(stats_frame, "COMPLETED", "0 ORDERS", "✅")

    def create_card(self, parent, title, value, icon):
        card = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
        card.pack(side="left", fill="both", expand=True, padx=10)

        # Icon
        tk.Label(card, text=icon, font=("Segoe UI", 24), bg=CARD_COLOR, fg=TEXT_WHITE).pack(side="right", anchor="n")

        # Text
        tk.Label(card, text=title, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#FFAAAA").pack(anchor="w")
        value_label = tk.Label(card, text=value, font=("Segoe UI", 22, "bold"), bg=CARD_COLOR, fg=TEXT_WHITE)
        value_label.pack(anchor="w")
        return value_label

    def update_stats(self):
        """Compute and update stats from backend orders.

        Definitions:
        - Pending: status PENDING or PROCESSING
        - Completed: status COMPLETED
        - Revenue: sum of totals for completed orders
        """
        try:
            orders = load_orders()

            # defensive: constants from OrderClass if available
            completed_const = getattr(OrderClass, 'COMPLETED', 'COMPLETED')
            pending_consts = {getattr(OrderClass, 'PENDING', 'PENDING'), getattr(OrderClass, 'PROCESSING', 'PROCESSING')}

            completed_orders = [o for o in orders if getattr(o, 'status', '').upper() == completed_const]
            pending_orders = [o for o in orders if getattr(o, 'status', '').upper() in pending_consts]

            # revenue: sum totals of completed orders
            total_revenue = 0.0
            for o in completed_orders:
                if hasattr(o, 'get_total'):
                    try:
                        total_revenue += float(o.get_total())
                    except Exception:
                        pass

            completed_count = len(completed_orders)
            pending_count = len(pending_orders)

            # update labels (safe-checks)
            if 'revenue' in self.stat_labels:
                self.stat_labels['revenue'].config(text=f"${total_revenue:,.2f}")
            if 'pending' in self.stat_labels:
                self.stat_labels['pending'].config(text=f"{pending_count} ORDERS")
            if 'completed' in self.stat_labels:
                self.stat_labels['completed'].config(text=f"{completed_count} ORDERS")
        except Exception:
            # fallback: show zeros (safe)
            if 'revenue' in getattr(self, 'stat_labels', {}):
                self.stat_labels['revenue'].config(text="$0.00")
            if 'pending' in getattr(self, 'stat_labels', {}):
                self.stat_labels['pending'].config(text="0 ORDERS")
            if 'completed' in getattr(self, 'stat_labels', {}):
                self.stat_labels['completed'].config(text="0 ORDERS")

    # ----------------------
    # Live Queue Section
    # ----------------------
    def build_queue_section(self):
        """Build kitchen and waiter queue display"""
        queue_label = tk.Label(self.main_area, text="LIVE QUEUE STATUS",
                              font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=TEXT_WHITE)
        queue_label.pack(anchor="w", pady=(10, 5))

        queue_container = tk.Frame(self.main_area, bg=BG_COLOR)
        queue_container.pack(fill="x", pady=(0, 15))

        # Kitchen Queue (Left)
        kitchen_frame = tk.Frame(queue_container, bg=CARD_COLOR, padx=15, pady=10)
        kitchen_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(kitchen_frame, text="👨‍🍳 KITCHEN QUEUE", font=("Segoe UI", 10, "bold"),
                bg=CARD_COLOR, fg="#FFD700").pack(anchor="w", pady=(0, 8))

        self.kitchen_canvas = tk.Canvas(kitchen_frame, bg="#3D0808", height=110, highlightthickness=0)
        self.kitchen_canvas.pack(fill="both", expand=True)

        # Waiter Queue (Right)
        waiter_frame = tk.Frame(queue_container, bg=CARD_COLOR, padx=15, pady=10)
        waiter_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        tk.Label(waiter_frame, text="🧑‍💼 WAITER/POS QUEUE", font=("Segoe UI", 10, "bold"),
                bg=CARD_COLOR, fg="#00BCD4").pack(anchor="w", pady=(0, 8))

        self.waiter_canvas = tk.Canvas(waiter_frame, bg="#3D0808", height=110, highlightthickness=0)
        self.waiter_canvas.pack(fill="both", expand=True)

    def refresh_queues(self):
        """Refresh kitchen and waiter queues and update stats"""
        try:
            orders = load_orders()

            kitchen_orders = [o for o in orders if getattr(o, 'status', '').upper() in
                              (getattr(OrderClass, 'PENDING', 'PENDING'), getattr(OrderClass, 'PROCESSING', 'PROCESSING'))]
            waiter_orders = [o for o in orders if getattr(o, 'status', '').upper() == getattr(OrderClass, 'DRAFT', 'DRAFT')]

            self.update_queue_display(self.kitchen_canvas, kitchen_orders, "Kitchen")
            self.update_queue_display(self.waiter_canvas, waiter_orders, "Waiter")
        except Exception:
            # Fallback with sample data
            sample_kitchen = ["ORD-1001 (4 items)", "ORD-1002 (2 items)"]
            sample_waiter = ["ORD-1003 (3 items)"]
            self.update_queue_display_simple(self.kitchen_canvas, sample_kitchen)
            self.update_queue_display_simple(self.waiter_canvas, sample_waiter)

        # update stats too
        try:
            self.update_stats()
        except Exception:
            pass

        # Schedule next refresh
        self.after(2000, self.refresh_queues)

    def update_queue_display(self, canvas, orders, queue_type):
        """Update queue canvas with order information"""
        canvas.delete("all")

        if not orders:
            canvas.create_text(150, 50, text=f"No {queue_type} Orders",
                               font=("Segoe UI", 11), fill="#FFAAAA")
            return

        # draw up to 4 compact order lines
        y_offset = 10
        width = int(canvas.winfo_width() or 300)
        box_w = min(320, width - 10)
        for i, order in enumerate(orders[:4]):
            items_count = len(order.items) if hasattr(order, 'items') else 0
            status_text = getattr(order, 'status', 'PENDING')

            # Order background
            canvas.create_rectangle(5, y_offset, 5 + box_w, y_offset + 30, fill="#450A0A", outline="#FF6B6B")

            # Order text
            canvas.create_text(12, y_offset + 4, text=f"{order.order_id}",
                               font=("Segoe UI", 9, "bold"), fill=ACCENT_GOLD, anchor="nw")
            canvas.create_text(12, y_offset + 18, text=f"{items_count} items  •  {status_text}",
                               font=("Segoe UI", 8), fill=TEXT_WHITE, anchor="nw")

            y_offset += 36

    def update_queue_display_simple(self, canvas, orders):
        """Update queue with simple sample data"""
        canvas.delete("all")

        if not orders:
            canvas.create_text(150, 50, text="No Orders",
                               font=("Segoe UI", 11), fill="#FFAAAA")
            return

        y_offset = 10
        width = int(canvas.winfo_width() or 300)
        box_w = min(320, width - 10)
        for order in orders[:4]:
            canvas.create_rectangle(5, y_offset, 5 + box_w, y_offset + 30, fill="#450A0A", outline="#FF6B6B")
            canvas.create_text(12, y_offset + 15, text=order,
                               font=("Segoe UI", 9, "bold"), fill=ACCENT_GOLD, anchor="w")
            y_offset += 36

    # ----------------------
    # Orders Table (main list) - ORDER ID and CUSTOMER removed
    # ----------------------
    def build_table_section(self):
        # New headers (without ORDER ID and CUSTOMER)
        headers = ["DATE & TIME", "ITEMS", "TOTAL", "STATUS"]

        table_frame = tk.Frame(self.main_area, bg=CARD_COLOR, padx=20, pady=20)
        table_frame.pack(fill="both", expand=True)

        # Header Row
        header_row = tk.Frame(table_frame, bg=CARD_COLOR)
        header_row.pack(fill="x", pady=(0, 10))
        for col in headers:
            tk.Label(header_row, text=col, font=("Segoe UI", 10, "bold"),
                     bg=CARD_COLOR, fg="#FFAAAA", width=20, anchor="w").pack(side="left", fill="x", expand=True)

        # Separator
        tk.Frame(table_frame, bg="#883333", height=2).pack(fill="x", pady=(0, 10))

        # Orders area (scrollable)
        orders_area = tk.Frame(table_frame, bg=CARD_COLOR)
        orders_area.pack(fill="both", expand=True)

        # Create a scrollbar + canvas to hold rows
        canvas = tk.Canvas(orders_area, bg=CARD_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(orders_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=CARD_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate with current orders from backend (if available) otherwise sample
        try:
            orders = load_orders()
            data_rows = []
            for o in orders:
                created = getattr(o, 'created_at', None)
                created_str = created.strftime("%b %d, %H:%M") if created else "-"
                items_text = ", ".join([f"{it.name} x{it.quantity}" if hasattr(it, 'name') else "item" for it in getattr(o, 'items', [])])
                total = 0.0
                if hasattr(o, 'get_total'):
                    try:
                        total = o.get_total()
                    except Exception:
                        total = 0.0
                status = getattr(o, 'status', '-')
                # Only include DATE & TIME, ITEMS, TOTAL, STATUS
                data_rows.append((created_str, items_text or "-", f"${total:.2f}", status))
        except Exception:
            # sample fallback (only date, items, total, status)
            data_rows = [
                ("Oct 26, 18:30", "Burger, Salad", "$34.50", "Completed"),
                ("Oct 26, 18:35", "Steak, Wine", "$85.00", "Completed"),
                ("Oct 26, 18:40", "Pizza, Coke", "$22.00", "Completed"),
                ("Oct 26, 18:45", "Pasta", "$18.00", "Completed"),
            ]

        for row in data_rows:
            row_frame = tk.Frame(scrollable_frame, bg=CARD_COLOR)
            row_frame.pack(fill="x", pady=5)
            for item in row:
                tk.Label(row_frame, text=item, font=("Segoe UI", 10),
                         bg=CARD_COLOR, fg="white", width=20, anchor="w").pack(side="left", fill="x", expand=True)

            # Thin separator line
            tk.Frame(scrollable_frame, bg="#441111", height=1).pack(fill="x", pady=2)

    # ----------------------
    # Reports / Analytics window (remove Order ID and Customer)
    # ----------------------
    def open_reports_analytics(self, event=None):
        """Open reports and analytics window (a summarized view)"""
        reports_window = tk.Toplevel(self)
        reports_window.title("Orders & Statistics")
        reports_window.geometry("900x700")
        reports_window.configure(bg=BG_COLOR)

        # Title
        title_label = tk.Label(reports_window, text="Orders & Analytics Dashboard",
                               font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_WHITE)
        title_label.pack(pady=10)

        # Main container
        main_container = tk.Frame(reports_window, bg=BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Left side - Statistics Cards
        left_frame = tk.Frame(main_container, bg=BG_COLOR)
        left_frame.pack(side="left", fill="both", padx=(0, 5))

        tk.Label(left_frame, text="Statistics", font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 5))

        # Build stats from backend (use consistent definitions)
        try:
            orders = load_orders()
            total_orders = len(orders)

            completed_const = getattr(OrderClass, 'COMPLETED', 'COMPLETED')
            pending_consts = {getattr(OrderClass, 'PENDING', 'PENDING'), getattr(OrderClass, 'PROCESSING', 'PROCESSING')}
            completed_orders = [o for o in orders if getattr(o, 'status', '').upper() == completed_const]
            pending_orders = [o for o in orders if getattr(o, 'status', '').upper() in pending_consts]
            total_revenue = sum((o.get_total() if hasattr(o, 'get_total') else 0) for o in completed_orders)
        except Exception:
            total_revenue = 0
            completed_orders = []
            pending_orders = []
            total_orders = 0

        stats_data = [
            ("Total Orders", str(total_orders), ACCENT_GOLD),
            ("Completed", str(len(completed_orders)), ACCENT_GREEN),
            ("Pending", str(len(pending_orders)), "#FF9800"),
            ("Total Revenue", f"${total_revenue:,.2f}", ACCENT_GOLD),
        ]

        for title, value, color in stats_data:
            stat_card = tk.Frame(left_frame, bg=CARD_COLOR, padx=15, pady=12)
            stat_card.pack(fill="x", pady=5)

            tk.Label(stat_card, text=title, font=("Segoe UI", 9),
                     bg=CARD_COLOR, fg="#FFAAAA").pack(anchor="w")
            tk.Label(stat_card, text=value, font=("Segoe UI", 14, "bold"),
                     bg=CARD_COLOR, fg=color).pack(anchor="w")

        # Right side - brief recent orders list (without Order ID & Customer)
        right_frame = tk.Frame(main_container, bg=BG_COLOR)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        tk.Label(right_frame, text="Recent Orders", font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 5))

        # Orders table frame
        table_frame = tk.Frame(right_frame, bg=CARD_COLOR, padx=8, pady=8)
        table_frame.pack(fill="both", expand=True)

        # Table headers (DATE/TIME, ITEMS, TOTAL, STATUS)
        headers = ["DATE & TIME", "ITEMS", "TOTAL", "STATUS"]
        header_frame = tk.Frame(table_frame, bg=CARD_COLOR)
        header_frame.pack(fill="x", pady=(0, 8))

        for header in headers:
            tk.Label(header_frame, text=header, font=("Segoe UI", 9, "bold"),
                     bg=CARD_COLOR, fg="#FFAAAA", width=20, anchor="w").pack(side="left", fill="x", expand=True)

        # Separator
        tk.Frame(table_frame, bg="#883333", height=1).pack(fill="x", pady=(0, 8))

        # Scrollable orders list
        scroll_frame = tk.Frame(table_frame, bg=CARD_COLOR)
        scroll_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_frame, bg=SIDEBAR_COLOR)
        scrollbar.pack(side="right", fill="y")

        orders_listbox = tk.Listbox(scroll_frame, bg="#3D0808", fg=TEXT_WHITE,
                                    font=("Segoe UI", 8), height=20, yscrollcommand=scrollbar.set)
        orders_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=orders_listbox.yview)

        # Recent orders (DATE/TIME, ITEMS, TOTAL, STATUS)
        try:
            recent = load_orders()[-20:]
            for o in reversed(recent):
                created = getattr(o, 'created_at', None)
                created_str = created.strftime("%b %d, %H:%M") if created else "-"
                items_text = ", ".join([getattr(it, 'name', 'item') for it in getattr(o, 'items', [])])
                total = o.get_total() if hasattr(o, 'get_total') else 0
                status = getattr(o, 'status', '-')
                text = f"{created_str:<15} | {items_text:<30} | ${total:.2f} | {status}"
                orders_listbox.insert(tk.END, text)
        except Exception:
            sample_orders = [
                ("Oct 26, 18:30", "Burger, Salad", "$34.50", "✓ Completed"),
                ("Oct 26, 18:35", "Steak, Wine", "$85.00", "✓ Completed"),
                ("Oct 26, 18:40", "Pizza, Coke", "$22.00", "✓ Completed"),
            ]
            for order in sample_orders:
                orders_listbox.insert(tk.END, f"{order[0]:<15} | {order[1]:<30} | {order[2]:<8} | {order[3]}")

        # Close button
        close_btn = tk.Button(reports_window, text="Close", command=reports_window.destroy,
                              bg="#6A0D0D", fg="white", font=("Segoe UI", 10, "bold"),
                              padx=15, pady=6, relief="flat", cursor="hand2")
        close_btn.pack(side="bottom", pady=5)

    # ----------------------
    # Menu management (simple)
    # ----------------------
    def open_menu_management(self, event=None):
        """Open menu items management window"""
        menu_window = tk.Toplevel(self)
        menu_window.title("Manage Menu Items")
        menu_window.geometry("550x500")
        menu_window.configure(bg=BG_COLOR)

        # Title
        title_label = tk.Label(menu_window, text="Menu Management",
                              font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_WHITE)
        title_label.pack(pady=10)

        # Frame for menu items list
        list_frame = tk.Frame(menu_window, bg=CARD_COLOR, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        tk.Label(list_frame, text="Menu Items:", font=("Segoe UI", 10, "bold"),
                bg=CARD_COLOR, fg="#FFAAAA").pack(anchor="w")

        # Listbox for menu items with scrollbar
        scroll_frame = tk.Frame(list_frame, bg=CARD_COLOR)
        scroll_frame.pack(fill="both", expand=True, pady=(5, 10))

        scrollbar = tk.Scrollbar(scroll_frame, bg=SIDEBAR_COLOR)
        scrollbar.pack(side="right", fill="y")

        self.menu_listbox = tk.Listbox(scroll_frame, bg="#3D0808", fg=TEXT_WHITE,
                                       font=("Segoe UI", 10), height=12, yscrollcommand=scrollbar.set)
        self.menu_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.menu_listbox.yview)

        # Load sample menu items
        sample_items = [
            "Pizza - $12.99",
            "Burger - $10.50",
            "Pasta - $14.99",
            "Salad - $8.99",
            "Steak - $22.99",
            "Chicken - $16.99"
        ]
        for item in sample_items:
            self.menu_listbox.insert(tk.END, item)

        # Bottom section with stats and actions
        bottom_frame = tk.Frame(menu_window, bg=BG_COLOR)
        bottom_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Stats section
        stats_frame = tk.Frame(bottom_frame, bg=CARD_COLOR, padx=10, pady=8)
        stats_frame.pack(fill="x", pady=(0, 10))

        tk.Label(stats_frame, text=f"Total Items: {len(sample_items)}", font=("Segoe UI", 9),
                bg=CARD_COLOR, fg=ACCENT_GOLD).pack(side="left", padx=15)

        # Button frame with better layout
        btn_frame = tk.Frame(bottom_frame, bg=BG_COLOR)
        btn_frame.pack(fill="x")

        # Left buttons
        left_btn_frame = tk.Frame(btn_frame, bg=BG_COLOR)
        left_btn_frame.pack(side="left", fill="x", expand=True)

        add_item_btn = tk.Button(left_btn_frame, text="+ Add Item", command=self.add_menu_item,
                                bg=ACCENT_GREEN, fg="white", font=("Segoe UI", 10, "bold"),
                                padx=12, pady=6, relief="flat", cursor="hand2")
        add_item_btn.pack(side="left", padx=3)

        remove_item_btn = tk.Button(left_btn_frame, text="- Remove", command=self.remove_menu_item,
                                   bg="#DC3545", fg="white", font=("Segoe UI", 10, "bold"),
                                   padx=12, pady=6, relief="flat", cursor="hand2")
        remove_item_btn.pack(side="left", padx=3)

        edit_item_btn = tk.Button(left_btn_frame, text="✎ Edit", command=self.edit_menu_item,
                                 bg=ACCENT_GOLD, fg="#000000", font=("Segoe UI", 10, "bold"),
                                 padx=12, pady=6, relief="flat", cursor="hand2")
        edit_item_btn.pack(side="left", padx=3)

        # Right buttons
        right_btn_frame = tk.Frame(btn_frame, bg=BG_COLOR)
        right_btn_frame.pack(side="right", fill="x")

        close_btn = tk.Button(right_btn_frame, text="Close", command=menu_window.destroy,
                             bg="#6A0D0D", fg="white", font=("Segoe UI", 10, "bold"),
                             padx=12, pady=6, relief="flat", cursor="hand2")
        close_btn.pack(side="right", padx=3)

    def add_menu_item(self):
        """Add a new menu item"""
        try:
            item_name = simpledialog.askstring("Add Item", "Enter item name (e.g., Pizza):")
            if item_name:
                price = simpledialog.askstring("Add Item", "Enter price (e.g., 12.99):")
                if price:
                    float(price)  # validate
                    new_item = f"{item_name} - ${price}"
                    if hasattr(self, 'menu_listbox') and new_item not in self.menu_listbox.get(0, tk.END):
                        self.menu_listbox.insert(tk.END, new_item)
                        messagebox.showinfo("Success", f"Item '{item_name}' added successfully!")
                    else:
                        messagebox.showwarning("Warning", "Item already exists!")
        except ValueError:
            messagebox.showerror("Error", "Invalid price format!")

    def remove_menu_item(self):
        """Remove selected menu item"""
        if not hasattr(self, 'menu_listbox'):
            return
        selection = self.menu_listbox.curselection()
        if selection:
            item = self.menu_listbox.get(selection[0])
            self.menu_listbox.delete(selection[0])
            messagebox.showinfo("Success", f"Item '{item}' removed successfully!")
        else:
            messagebox.showwarning("Warning", "Please select an item to remove!")

    def edit_menu_item(self):
        """Edit selected menu item"""
        if not hasattr(self, 'menu_listbox'):
            return
        selection = self.menu_listbox.curselection()
        if selection:
            old_item = self.menu_listbox.get(selection[0])
            new_name = simpledialog.askstring("Edit Item", f"Enter new name for '{old_item}':")
            if new_name:
                new_price = simpledialog.askstring("Edit Item", "Enter new price:")
                try:
                    float(new_price)
                    new_item = f"{new_name} - ${new_price}"
                    self.menu_listbox.delete(selection[0])
                    self.menu_listbox.insert(selection[0], new_item)
                    messagebox.showinfo("Success", f"Item updated to '{new_name}'!")
                except ValueError:
                    messagebox.showerror("Error", "Invalid price format!")
        else:
            messagebox.showwarning("Warning", "Please select an item to edit!")

    # ----------------------
    # Users management (simple)
    # ----------------------
    def open_users_management(self, event=None):
        """Open users management window"""
        users_window = tk.Toplevel(self)
        users_window.title("Manage Users")
        users_window.geometry("550x500")
        users_window.configure(bg=BG_COLOR)

        # Title
        title_label = tk.Label(users_window, text="User Management",
                              font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_WHITE)
        title_label.pack(pady=10)

        # Frame for user list
        list_frame = tk.Frame(users_window, bg=CARD_COLOR, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        tk.Label(list_frame, text="Current Users:", font=("Segoe UI", 10, "bold"),
                bg=CARD_COLOR, fg="#FFAAAA").pack(anchor="w")

        # Listbox for users with scrollbar
        scroll_frame = tk.Frame(list_frame, bg=CARD_COLOR)
        scroll_frame.pack(fill="both", expand=True, pady=(5, 10))

        scrollbar = tk.Scrollbar(scroll_frame, bg=SIDEBAR_COLOR)
        scrollbar.pack(side="right", fill="y")

        self.users_listbox = tk.Listbox(scroll_frame, bg="#3D0808", fg=TEXT_WHITE,
                                        font=("Segoe UI", 10), height=12, yscrollcommand=scrollbar.set)
        self.users_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.users_listbox.yview)

        # Load sample users
        sample_users = ["Admin User", "Chef1", "Waiter1", "Manager1"]
        for user in sample_users:
            self.users_listbox.insert(tk.END, user)

        # Bottom section with stats and actions
        bottom_frame = tk.Frame(users_window, bg=BG_COLOR)
        bottom_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Stats section
        stats_frame = tk.Frame(bottom_frame, bg=CARD_COLOR, padx=10, pady=8)
        stats_frame.pack(fill="x", pady=(0, 10))

        tk.Label(stats_frame, text=f"Total Users: {len(sample_users)}", font=("Segoe UI", 9),
                bg=CARD_COLOR, fg=ACCENT_GOLD).pack(side="left", padx=15)

        # Button frame with better layout
        btn_frame = tk.Frame(bottom_frame, bg=BG_COLOR)
        btn_frame.pack(fill="x")

        # Left buttons
        left_btn_frame = tk.Frame(btn_frame, bg=BG_COLOR)
        left_btn_frame.pack(side="left", fill="x", expand=True)

        add_btn = tk.Button(left_btn_frame, text="+ Add User", command=self.add_user,
                           bg=ACCENT_GREEN, fg="white", font=("Segoe UI", 10, "bold"),
                           padx=12, pady=6, relief="flat", cursor="hand2")
        add_btn.pack(side="left", padx=3)

        remove_btn = tk.Button(left_btn_frame, text="- Remove", command=self.remove_user,
                              bg="#DC3545", fg="white", font=("Segoe UI", 10, "bold"),
                              padx=12, pady=6, relief="flat", cursor="hand2")
        remove_btn.pack(side="left", padx=3)

        edit_btn = tk.Button(left_btn_frame, text="✎ Edit", command=self.edit_user,
                            bg=ACCENT_GOLD, fg="#000000", font=("Segoe UI", 10, "bold"),
                            padx=12, pady=6, relief="flat", cursor="hand2")
        edit_btn.pack(side="left", padx=3)

        # Right buttons
        right_btn_frame = tk.Frame(btn_frame, bg=BG_COLOR)
        right_btn_frame.pack(side="right", fill="x")

        close_btn = tk.Button(right_btn_frame, text="Close", command=users_window.destroy,
                             bg="#6A0D0D", fg="white", font=("Segoe UI", 10, "bold"),
                             padx=12, pady=6, relief="flat", cursor="hand2")
        close_btn.pack(side="right", padx=3)

    def add_user(self):
        """Add a new user"""
        username = simpledialog.askstring("Add User", "Enter username:")
        if username:
            if username not in self.users_listbox.get(0, tk.END):
                self.users_listbox.insert(tk.END, username)
                messagebox.showinfo("Success", f"User '{username}' added successfully!")
            else:
                messagebox.showwarning("Warning", "User already exists!")

    def remove_user(self):
        """Remove selected user"""
        selection = self.users_listbox.curselection()
        if selection:
            username = self.users_listbox.get(selection[0])
            self.users_listbox.delete(selection[0])
            messagebox.showinfo("Success", f"User '{username}' removed successfully!")
        else:
            messagebox.showwarning("Warning", "Please select a user to remove!")

    def edit_user(self):
        """Edit selected user"""
        selection = self.users_listbox.curselection()
        if selection:
            old_username = self.users_listbox.get(selection[0])
            new_username = simpledialog.askstring("Edit User", f"Enter new username for '{old_username}':")
            if new_username:
                self.users_listbox.delete(selection[0])
                self.users_listbox.insert(selection[0], new_username)
                messagebox.showinfo("Success", f"User updated to '{new_username}'!")
        else:
            messagebox.showwarning("Warning", "Please select a user to edit!")

# --- TEST BLOCK ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AdminDashboard()
    root.mainloop()