import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from collections import Counter
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.order import load_orders, Order as OrderClass
from backend.user import load_users, save_users, Admin, Waiter, Chef, User
from backend.menuitem import load_menu_items, save_menu_items, MenuItem

# --- COLORS ---
BG_COLOR = "#2B0505"       
SIDEBAR_COLOR = "#450A0A"  
CARD_COLOR = "#6A0D0D"     
TEXT_WHITE = "#FFFFFF"
ACCENT_GOLD = "#FFD700"
ACCENT_GREEN = "#28a745"
ACCENT_BLUE = "#0D6EFD"
ACCENT_RED = "#DC3545"

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

        self.stat_labels = {}
        self.table_scrollable_frame = None 
        self.last_table_hash = None        
        self.table_window_id = None # Store ID to resize window

        self.build_stats_row()
        self.build_queue_section()
        self.build_table_structure()       

        # Start auto-refresh
        self.refresh_timer()

    def build_sidebar_icons(self):
        icons = ["📋", "📊", "👥"]

        tk.Label(self.sidebar, text="ADMIN", font=("Segoe UI", 15), bg=SIDEBAR_COLOR, fg="white").pack(pady=20)

        for icon in icons:
            btn = tk.Label(self.sidebar, text=icon, font=("Segoe UI", 20),
                           bg=SIDEBAR_COLOR, fg="#AA5555", cursor="hand2")
            btn.pack(pady=15, fill="x")
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#AA5555"))

            if icon == "👥":
                btn.bind("<Button-1>", self.open_users_management)
            elif icon == "📋":
                btn.bind("<Button-1>", self.open_menu_management)
            elif icon == "📊":
                btn.bind("<Button-1>", self.open_reports_analytics)

    # ----------------------
    # Live Stats
    # ----------------------
    def build_stats_row(self):
        stats_frame = tk.Frame(self.main_area, bg=BG_COLOR)
        stats_frame.pack(fill="x", pady=(0, 10))

        self.stat_labels['revenue'] = self.create_card(stats_frame, "REVENUE", "$0.00", "💲")
        self.stat_labels['pending'] = self.create_card(stats_frame, "PENDING", "0 ORDERS", "🕒")
        self.stat_labels['completed'] = self.create_card(stats_frame, "COMPLETED", "0 ORDERS", "✅")

    def create_card(self, parent, title, value, icon):
        card = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
        card.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(card, text=icon, font=("Segoe UI", 24), bg=CARD_COLOR, fg=TEXT_WHITE).pack(side="right", anchor="n")
        tk.Label(card, text=title, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#FFAAAA").pack(anchor="w")
        value_label = tk.Label(card, text=value, font=("Segoe UI", 22, "bold"), bg=CARD_COLOR, fg=TEXT_WHITE)
        value_label.pack(anchor="w")
        return value_label

    def update_stats(self, orders):
        try:
            completed_orders = [o for o in orders if o.status == OrderClass.COMPLETED]
            pending_orders = [o for o in orders if o.status in [OrderClass.PENDING, OrderClass.PROCESSING]]

            total_revenue = sum(o.get_total() for o in completed_orders)

            self.stat_labels['revenue'].config(text=f"${total_revenue:,.2f}")
            self.stat_labels['pending'].config(text=f"{len(pending_orders)} ORDERS")
            self.stat_labels['completed'].config(text=f"{len(completed_orders)} ORDERS")
        except Exception:
            pass

    # ----------------------
    # Live Queue Section
    # ----------------------
    def build_queue_section(self):
        queue_label = tk.Label(self.main_area, text="LIVE KITCHEN QUEUE",
                              font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=TEXT_WHITE)
        queue_label.pack(anchor="w", pady=(10, 5))

        queue_container = tk.Frame(self.main_area, bg=BG_COLOR)
        queue_container.pack(fill="x", pady=(0, 15))

        kitchen_frame = tk.Frame(queue_container, bg=CARD_COLOR, padx=15, pady=10)
        kitchen_frame.pack(fill="both", expand=True)

        tk.Label(kitchen_frame, text="👨‍🍳 ACTIVE ORDERS", font=("Segoe UI", 10, "bold"),
                bg=CARD_COLOR, fg="#FFD700").pack(anchor="w", pady=(0, 8))

        self.kitchen_canvas = tk.Canvas(kitchen_frame, bg="#3D0808", height=120, highlightthickness=0)
        self.kitchen_canvas.pack(fill="both", expand=True)

    def update_queue_display(self, orders):
        kitchen_orders = [o for o in orders if o.status in [OrderClass.PENDING, OrderClass.PROCESSING]]
        
        self.kitchen_canvas.delete("all")

        if not kitchen_orders:
            self.kitchen_canvas.create_text(self.kitchen_canvas.winfo_width()/2, 60, text="No Active Orders",
                               font=("Segoe UI", 11), fill="#FFAAAA", anchor="center")
            return

        x_offset = 10
        y_offset = 10
        card_w = 200
        card_h = 100
        
        for i, order in enumerate(kitchen_orders):
            if x_offset + card_w > self.kitchen_canvas.winfo_width(): break 

            items_count = len(order.items)
            status_text = order.status

            # Draw Card
            self.kitchen_canvas.create_rectangle(x_offset, y_offset, x_offset + card_w, y_offset + card_h, 
                                    fill="#450A0A", outline="#FF6B6B")
            
            self.kitchen_canvas.create_text(x_offset + 10, y_offset + 15, text=f"{order.order_id[-8:]}",
                               font=("Segoe UI", 10, "bold"), fill=ACCENT_GOLD, anchor="nw")
            
            self.kitchen_canvas.create_text(x_offset + 10, y_offset + 40, text=f"{order.customer_id}",
                               font=("Segoe UI", 9), fill="white", anchor="nw")

            self.kitchen_canvas.create_text(x_offset + 10, y_offset + 65, text=f"{items_count} items • {status_text}",
                               font=("Segoe UI", 8), fill="#CCCCCC", anchor="nw")

            x_offset += card_w + 10

    # ----------------------
    # Orders Table (GRID LAYOUT FIX)
    # ----------------------
    def build_table_structure(self):
        headers = ["DATE & TIME", "CUSTOMER", "ITEMS", "TOTAL", "STATUS"]

        table_frame = tk.Frame(self.main_area, bg=CARD_COLOR, padx=20, pady=20)
        table_frame.pack(fill="both", expand=True)

        # -- HEADERS (Using Grid) --
        header_row = tk.Frame(table_frame, bg=CARD_COLOR)
        header_row.pack(fill="x", pady=(0, 10))
        
        for i, col in enumerate(headers):
            # Items (index 2) gets weight 2, others weight 1
            weight = 2 if i == 2 else 1
            header_row.columnconfigure(i, weight=weight)
            
            tk.Label(header_row, text=col, font=("Segoe UI", 10, "bold"),
                     bg=CARD_COLOR, fg="#FFAAAA", anchor="w").grid(row=0, column=i, sticky="ew")

        tk.Frame(table_frame, bg="#883333", height=2).pack(fill="x", pady=(0, 10))

        # -- SCROLLABLE AREA --
        orders_area = tk.Frame(table_frame, bg=CARD_COLOR)
        orders_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(orders_area, bg=CARD_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(orders_area, orient="vertical", command=canvas.yview)
        
        self.table_scrollable_frame = tk.Frame(canvas, bg=CARD_COLOR)
        
        # --- CRITICAL FIX: Force inner frame to match canvas width ---
        self.table_window_id = canvas.create_window((0, 0), window=self.table_scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            # Update scrollregion
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Force width to match canvas
            canvas.itemconfig(self.table_window_id, width=event.width)

        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.update_table_content(load_orders())

    def update_table_content(self, orders):
        orders.sort(key=lambda x: x.created_at, reverse=True)

        current_hash = "".join([f"{o.order_id}{o.status}" for o in orders])
        if self.last_table_hash == current_hash:
            return 
        self.last_table_hash = current_hash

        for widget in self.table_scrollable_frame.winfo_children():
            widget.destroy()

        if not orders:
             tk.Label(self.table_scrollable_frame, text="No order history found.", bg=CARD_COLOR, fg="white").pack(pady=20)
             return

        # -- ROWS (Using Grid to match Headers) --
        for o in orders:
            created_str = o.created_at.strftime("%b %d, %H:%M")
            items_text = ", ".join([f"{it.name}" for it in o.items])
            if len(items_text) > 40: items_text = items_text[:37] + "..."
            total = o.get_total()
            
            row_frame = tk.Frame(self.table_scrollable_frame, bg=CARD_COLOR)
            row_frame.pack(fill="x", pady=5)
            
            data = [created_str, o.customer_id, items_text, f"${total:.2f}", o.status]
            
            status_color = "white"
            if o.status == OrderClass.COMPLETED: status_color = ACCENT_GREEN
            elif o.status == OrderClass.PENDING: status_color = "#FFC107"
            elif o.status == OrderClass.PROCESSING: status_color = ACCENT_BLUE

            for i, item in enumerate(data):
                weight = 2 if i == 2 else 1
                row_frame.columnconfigure(i, weight=weight)
                
                fg_color = status_color if i == 4 else "white"
                
                tk.Label(row_frame, text=item, font=("Segoe UI", 10),
                         bg=CARD_COLOR, fg=fg_color, anchor="w").grid(row=0, column=i, sticky="ew")
            
            tk.Frame(self.table_scrollable_frame, bg="#441111", height=1).pack(fill="x", pady=2)

    # ----------------------
    # Global Refresh Timer
    # ----------------------
    def refresh_timer(self):
        try:
            orders = load_orders()
            self.update_stats(orders)
            self.update_queue_display(orders)
            self.update_table_content(orders)
        except Exception as e:
            print(f"Refresh error: {e}")
        
        self.after(2000, self.refresh_timer)

    # ----------------------
    # Reports & Analytics Window
    # ----------------------
    def open_reports_analytics(self, event=None):
        win = tk.Toplevel(self)
        win.title("SmartChef - Detailed Analytics")
        win.geometry("1000x700")
        win.configure(bg=BG_COLOR)

        orders = load_orders()
        completed = [o for o in orders if o.status == OrderClass.COMPLETED]
        
        total_rev = sum(o.get_total() for o in completed)
        total_orders = len(orders)
        avg_order = total_rev / len(completed) if completed else 0
        
        all_items = []
        for o in orders:
            for i in o.items:
                all_items.append(i.name)
        
        counts = Counter(all_items)
        pop_item = counts.most_common(1)[0][0] if counts else "N/A"
        
        tk.Label(win, text="Analytics Dashboard", font=("Segoe UI", 24, "bold"), 
                 bg=BG_COLOR, fg=TEXT_WHITE).pack(pady=20)

        metrics_frame = tk.Frame(win, bg=BG_COLOR)
        metrics_frame.pack(fill="x", padx=20, pady=10)

        self.create_analytic_card(metrics_frame, "Total Revenue", f"${total_rev:,.2f}", ACCENT_GOLD)
        self.create_analytic_card(metrics_frame, "Total Orders", str(total_orders), ACCENT_BLUE)
        self.create_analytic_card(metrics_frame, "Avg Order Value", f"${avg_order:.2f}", ACCENT_GREEN)
        self.create_analytic_card(metrics_frame, "Popular Item", pop_item, ACCENT_RED)

        chart_frame = tk.Frame(win, bg=CARD_COLOR, padx=20, pady=20)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(chart_frame, text="Order Status Distribution", font=("Segoe UI", 14, "bold"), 
                 bg=CARD_COLOR, fg="white").pack(anchor="w", pady=(0, 10))

        self.draw_status_chart(chart_frame, orders)

    def create_analytic_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=CARD_COLOR, padx=15, pady=15)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(card, text=title, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#CCC").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg=CARD_COLOR, fg=color).pack(anchor="w")

    def draw_status_chart(self, parent, orders):
        canvas = tk.Canvas(parent, bg=BG_COLOR, height=250, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        statuses = [o.status for o in orders]
        c = Counter(statuses)
        data = {
            "Completed": c.get(OrderClass.COMPLETED, 0),
            "Pending": c.get(OrderClass.PENDING, 0) + c.get(OrderClass.PROCESSING, 0),
            "Draft/Other": c.get(OrderClass.DRAFT, 0)
        }
        
        max_val = max(data.values()) if data.values() else 1
        w = 800
        h = 200
        bar_width = 100
        gap = 50
        x_start = 50
        colors = {"Completed": ACCENT_GREEN, "Pending": ACCENT_BLUE, "Draft/Other": "#777"}
        
        for i, (label, val) in enumerate(data.items()):
            bar_h = (val / max_val) * (h - 40)
            x = x_start + i * (bar_width + gap)
            y_top = h - bar_h
            
            canvas.create_rectangle(x, y_top, x + bar_width, h, fill=colors[label], outline="")
            canvas.create_text(x + bar_width/2, y_top - 10, text=str(val), fill="white", font=("Segoe UI", 10, "bold"))
            canvas.create_text(x + bar_width/2, h + 15, text=label, fill="#CCC", font=("Segoe UI", 10))

    # ----------------------
    # MENU MANAGEMENT
    # ----------------------
    def open_menu_management(self, event=None):
        self.menu_window = tk.Toplevel(self)
        self.menu_window.title("Manage Menu Items")
        self.menu_window.geometry("600x600")
        self.menu_window.configure(bg=BG_COLOR)

        tk.Label(self.menu_window, text="Menu Management", font=("Segoe UI", 16, "bold"), 
                 bg=BG_COLOR, fg=TEXT_WHITE).pack(pady=10)

        list_frame = tk.Frame(self.menu_window, bg=CARD_COLOR, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10)

        scrollbar = tk.Scrollbar(list_frame, bg=SIDEBAR_COLOR)
        scrollbar.pack(side="right", fill="y")

        self.menu_listbox = tk.Listbox(list_frame, bg="#3D0808", fg=TEXT_WHITE,
                                       font=("Segoe UI", 10), height=15, yscrollcommand=scrollbar.set)
        self.menu_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.menu_listbox.yview)

        self.load_menu_list()

        btn_frame = tk.Frame(self.menu_window, bg=BG_COLOR, pady=10)
        btn_frame.pack(fill="x", padx=10)

        tk.Button(btn_frame, text="+ Add Item", command=self.add_menu_item_dialog, bg=ACCENT_GREEN, fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="- Remove", command=self.remove_menu_item, bg="#DC3545", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Close", command=self.menu_window.destroy, bg="#6A0D0D", fg="white").pack(side="right", padx=5)

    def load_menu_list(self):
        self.menu_listbox.delete(0, tk.END)
        self.menu_items = load_menu_items()
        for item in self.menu_items:
            self.menu_listbox.insert(tk.END, f"{item.id} | {item.name} | {item.category} | ${item.price}")

    def add_menu_item_dialog(self):
        dialog = tk.Toplevel(self.menu_window)
        dialog.title("Add Menu Item")
        dialog.geometry("300x350")
        dialog.configure(bg=BG_COLOR)

        fields = ["ID", "Name", "Category", "Price"]
        entries = {}

        for f in fields:
            tk.Label(dialog, text=f, bg=BG_COLOR, fg="white").pack(anchor="w", padx=20, pady=(10,0))
            e = tk.Entry(dialog)
            e.pack(fill="x", padx=20)
            entries[f] = e

        def save():
            try:
                item = MenuItem(
                    entries["ID"].get(),
                    entries["Name"].get(),
                    entries["Category"].get(),
                    float(entries["Price"].get())
                )
                if any(x.id == item.id for x in self.menu_items):
                    messagebox.showerror("Error", "ID already exists!")
                    return

                self.menu_items.append(item)
                save_menu_items(self.menu_items)
                self.load_menu_list()
                dialog.destroy()
                messagebox.showinfo("Success", "Item Added")
            except ValueError:
                messagebox.showerror("Error", "Invalid Price")

        tk.Button(dialog, text="Save", command=save, bg=ACCENT_GREEN, fg="white").pack(pady=20)

    def remove_menu_item(self):
        sel = self.menu_listbox.curselection()
        if not sel: return
        
        idx = sel[0]
        del self.menu_items[idx]
        save_menu_items(self.menu_items)
        self.load_menu_list()
        messagebox.showinfo("Success", "Item Removed")

    # ----------------------
    # USERS MANAGEMENT
    # ----------------------
    def open_users_management(self, event=None):
        self.users_window = tk.Toplevel(self)
        self.users_window.title("Manage Users")
        self.users_window.geometry("500x500")
        self.users_window.configure(bg=BG_COLOR)

        tk.Label(self.users_window, text="User Management", font=("Segoe UI", 16, "bold"), 
                 bg=BG_COLOR, fg=TEXT_WHITE).pack(pady=10)

        list_frame = tk.Frame(self.users_window, bg=CARD_COLOR, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10)

        self.users_listbox = tk.Listbox(list_frame, bg="#3D0808", fg=TEXT_WHITE, font=("Segoe UI", 10))
        self.users_listbox.pack(fill="both", expand=True)

        self.load_users_list()

        btn_frame = tk.Frame(self.users_window, bg=BG_COLOR, pady=10)
        btn_frame.pack(fill="x", padx=10)

        tk.Button(btn_frame, text="+ Add User", command=self.add_user_dialog, bg=ACCENT_GREEN, fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="- Remove", command=self.remove_user, bg="#DC3545", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Close", command=self.users_window.destroy, bg="#6A0D0D", fg="white").pack(side="right", padx=5)

    def load_users_list(self):
        self.users_listbox.delete(0, tk.END)
        self.users = load_users()
        for u in self.users:
            self.users_listbox.insert(tk.END, f"{u.get_username()}  [{u.get_role()}]")

    def add_user_dialog(self):
        dialog = tk.Toplevel(self.users_window)
        dialog.title("Add User")
        dialog.geometry("300x350")
        dialog.configure(bg=BG_COLOR)

        tk.Label(dialog, text="Username", bg=BG_COLOR, fg="white").pack(anchor="w", padx=20, pady=(10,0))
        e_user = tk.Entry(dialog)
        e_user.pack(fill="x", padx=20)

        tk.Label(dialog, text="Password", bg=BG_COLOR, fg="white").pack(anchor="w", padx=20, pady=(10,0))
        e_pass = tk.Entry(dialog, show="*")
        e_pass.pack(fill="x", padx=20)

        tk.Label(dialog, text="Role", bg=BG_COLOR, fg="white").pack(anchor="w", padx=20, pady=(10,0))
        c_role = ttk.Combobox(dialog, values=["admin", "waiter", "chef"], state="readonly")
        c_role.current(1)
        c_role.pack(fill="x", padx=20)

        def save():
            uname = e_user.get()
            pword = e_pass.get()
            role = c_role.get()

            if not uname or not pword:
                messagebox.showerror("Error", "All fields required")
                return

            if any(u.get_username() == uname for u in self.users):
                messagebox.showerror("Error", "Username taken")
                return

            if role == "admin": new_u = Admin(uname, pword)
            elif role == "chef": new_u = Chef(uname, pword)
            else: new_u = Waiter(uname, pword)

            self.users.append(new_u)
            save_users(self.users)
            self.load_users_list()
            dialog.destroy()
            messagebox.showinfo("Success", "User Added")

        tk.Button(dialog, text="Create User", command=save, bg=ACCENT_GREEN, fg="white").pack(pady=20)

    def remove_user(self):
        sel = self.users_listbox.curselection()
        if not sel: return
        
        idx = sel[0]
        del self.users[idx]
        save_users(self.users)
        self.load_users_list()
        messagebox.showinfo("Success", "User Removed")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AdminDashboard()
    root.mainloop()