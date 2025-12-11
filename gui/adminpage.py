import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
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

        self.build_stats_row()
        self.build_queue_section()
        self.build_table_section()

        # Start auto-refresh
        self.refresh_queues()

    def build_sidebar_icons(self):
        # Icons: Menu, Reports, Users
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

    def update_stats(self):
        try:
            orders = load_orders()
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
        """Build kitchen queue display (Full Width)"""
        queue_label = tk.Label(self.main_area, text="LIVE KITCHEN QUEUE",
                              font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=TEXT_WHITE)
        queue_label.pack(anchor="w", pady=(10, 5))

        queue_container = tk.Frame(self.main_area, bg=BG_COLOR)
        queue_container.pack(fill="x", pady=(0, 15))

        # Kitchen Queue (Expanded to full width)
        kitchen_frame = tk.Frame(queue_container, bg=CARD_COLOR, padx=15, pady=10)
        kitchen_frame.pack(fill="both", expand=True)

        tk.Label(kitchen_frame, text="👨‍🍳 ACTIVE ORDERS", font=("Segoe UI", 10, "bold"),
                bg=CARD_COLOR, fg="#FFD700").pack(anchor="w", pady=(0, 8))

        self.kitchen_canvas = tk.Canvas(kitchen_frame, bg="#3D0808", height=120, highlightthickness=0)
        self.kitchen_canvas.pack(fill="both", expand=True)

    def refresh_queues(self):
        try:
            orders = load_orders()
            kitchen_orders = [o for o in orders if o.status in [OrderClass.PENDING, OrderClass.PROCESSING]]
            self.update_queue_display(self.kitchen_canvas, kitchen_orders)
        except Exception:
            pass
        
        self.update_stats()
        self.after(2000, self.refresh_queues)

    def update_queue_display(self, canvas, orders):
        canvas.delete("all")

        if not orders:
            canvas.create_text(canvas.winfo_width()/2, 60, text="No Active Orders",
                               font=("Segoe UI", 11), fill="#FFAAAA", anchor="center")
            return

        # Horizontal layout for full width
        x_offset = 10
        y_offset = 10
        card_w = 200
        card_h = 100
        
        for i, order in enumerate(orders):
            if x_offset + card_w > canvas.winfo_width(): break 

            items_count = len(order.items)
            status_text = order.status

            # Draw Card
            canvas.create_rectangle(x_offset, y_offset, x_offset + card_w, y_offset + card_h, 
                                    fill="#450A0A", outline="#FF6B6B")
            
            canvas.create_text(x_offset + 10, y_offset + 15, text=f"{order.order_id[-8:]}",
                               font=("Segoe UI", 10, "bold"), fill=ACCENT_GOLD, anchor="nw")
            
            canvas.create_text(x_offset + 10, y_offset + 40, text=f"{order.customer_id}",
                               font=("Segoe UI", 9), fill="white", anchor="nw")

            canvas.create_text(x_offset + 10, y_offset + 65, text=f"{items_count} items • {status_text}",
                               font=("Segoe UI", 8), fill="#CCCCCC", anchor="nw")

            x_offset += card_w + 10

    # ----------------------
    # Orders Table
    # ----------------------
    def build_table_section(self):
        headers = ["DATE & TIME", "ITEMS", "TOTAL", "STATUS"]

        table_frame = tk.Frame(self.main_area, bg=CARD_COLOR, padx=20, pady=20)
        table_frame.pack(fill="both", expand=True)

        header_row = tk.Frame(table_frame, bg=CARD_COLOR)
        header_row.pack(fill="x", pady=(0, 10))
        for col in headers:
            tk.Label(header_row, text=col, font=("Segoe UI", 10, "bold"),
                     bg=CARD_COLOR, fg="#FFAAAA", width=20, anchor="w").pack(side="left", fill="x", expand=True)

        tk.Frame(table_frame, bg="#883333", height=2).pack(fill="x", pady=(0, 10))

        orders_area = tk.Frame(table_frame, bg=CARD_COLOR)
        orders_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(orders_area, bg=CARD_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(orders_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=CARD_COLOR)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            orders = load_orders()[-15:] # Show last 15
            for o in reversed(orders):
                created_str = o.created_at.strftime("%b %d, %H:%M")
                items_text = ", ".join([f"{it.name}" for it in o.items])[:40]
                total = o.get_total()
                
                row_frame = tk.Frame(scrollable_frame, bg=CARD_COLOR)
                row_frame.pack(fill="x", pady=5)
                
                data = [created_str, items_text, f"${total:.2f}", o.status]
                for item in data:
                    tk.Label(row_frame, text=item, font=("Segoe UI", 10),
                             bg=CARD_COLOR, fg="white", width=20, anchor="w").pack(side="left", fill="x", expand=True)
                
                tk.Frame(scrollable_frame, bg="#441111", height=1).pack(fill="x", pady=2)
        except Exception:
            pass

    # ----------------------
    # Reports 
    # ----------------------
    def open_reports_analytics(self, event=None):
        messagebox.showinfo("Info", "Detailed Analytics Coming Soon.\nRefer to Dashboard for live stats.")

    # ----------------------
    # MENU MANAGEMENT (Connected to JSON)
    # ----------------------
    def open_menu_management(self, event=None):
        self.menu_window = tk.Toplevel(self)
        self.menu_window.title("Manage Menu Items")
        self.menu_window.geometry("600x600")
        self.menu_window.configure(bg=BG_COLOR)

        tk.Label(self.menu_window, text="Menu Management", font=("Segoe UI", 16, "bold"), 
                 bg=BG_COLOR, fg=TEXT_WHITE).pack(pady=10)

        # List
        list_frame = tk.Frame(self.menu_window, bg=CARD_COLOR, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10)

        scrollbar = tk.Scrollbar(list_frame, bg=SIDEBAR_COLOR)
        scrollbar.pack(side="right", fill="y")

        self.menu_listbox = tk.Listbox(list_frame, bg="#3D0808", fg=TEXT_WHITE,
                                       font=("Segoe UI", 10), height=15, yscrollcommand=scrollbar.set)
        self.menu_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.menu_listbox.yview)

        self.load_menu_list()

        # Buttons
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
        # Custom Dialog
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
                # Check for duplicate ID
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
        
        # Remove from list based on index
        idx = sel[0]
        del self.menu_items[idx]
        save_menu_items(self.menu_items)
        self.load_menu_list()
        messagebox.showinfo("Success", "Item Removed")

    # ----------------------
    # USERS MANAGEMENT (Connected to JSON)
    # ----------------------
    def open_users_management(self, event=None):
        self.users_window = tk.Toplevel(self)
        self.users_window.title("Manage Users")
        self.users_window.geometry("500x500")
        self.users_window.configure(bg=BG_COLOR)

        tk.Label(self.users_window, text="User Management", font=("Segoe UI", 16, "bold"), 
                 bg=BG_COLOR, fg=TEXT_WHITE).pack(pady=10)

        # List
        list_frame = tk.Frame(self.users_window, bg=CARD_COLOR, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10)

        self.users_listbox = tk.Listbox(list_frame, bg="#3D0808", fg=TEXT_WHITE, font=("Segoe UI", 10))
        self.users_listbox.pack(fill="both", expand=True)

        self.load_users_list()

        # Buttons
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
        # Prevent deleting the last admin if possible, but basic logic:
        del self.users[idx]
        save_users(self.users)
        self.load_users_list()
        messagebox.showinfo("Success", "User Removed")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AdminDashboard()
    root.mainloop()