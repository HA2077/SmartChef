import tkinter as tk
from tkinter import messagebox

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
        self.geometry("1100x700")
        self.configure(bg=BG_COLOR)
        
        # Sidebar
        self.sidebar = tk.Frame(self, bg=SIDEBAR_COLOR, width=80)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.build_sidebar_icons()

        # Main Content
        self.main_area = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        self.main_area.pack(side="right", fill="both", expand=True)

        self.build_stats_row()
        self.build_table_section()

    def build_sidebar_icons(self):
        # Fake Icons using text
        icons = ["≡", "📋", "📊", "👥", "⚙️"]
        
        # Logo placeholder
        tk.Label(self.sidebar, text="👨‍🍳", font=("Segoe UI", 30), bg=SIDEBAR_COLOR, fg="white").pack(pady=20)

        for icon in icons:
            btn = tk.Label(self.sidebar, text=icon, font=("Segoe UI", 20), 
                           bg=SIDEBAR_COLOR, fg="#AA5555", cursor="hand2")
            btn.pack(pady=15, fill="x")
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#AA5555"))
            
        # Logout at bottom
        tk.Label(self.sidebar, text="🚪", font=("Segoe UI", 20), 
                 bg=SIDEBAR_COLOR, fg="#AA5555", cursor="hand2").pack(side="bottom", pady=20)

    def build_stats_row(self):
        stats_frame = tk.Frame(self.main_area, bg=BG_COLOR)
        stats_frame.pack(fill="x", pady=(0, 20))

        self.create_card(stats_frame, "REVENUE", "$45,230.50", "💲")
        self.create_card(stats_frame, "PENDING", "15 ORDERS", "🕒")
        self.create_card(stats_frame, "COMPLETED", "124 ORDERS", "✅")

    def create_card(self, parent, title, value, icon):
        card = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        # Icon
        tk.Label(card, text=icon, font=("Segoe UI", 24), bg=CARD_COLOR, fg=TEXT_WHITE).pack(side="right", anchor="n")
        
        # Text
        tk.Label(card, text=title, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#FFAAAA").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 22, "bold"), bg=CARD_COLOR, fg=TEXT_WHITE).pack(anchor="w")

    def build_table_section(self):
        # Table Header
        headers = ["ORDER ID", "CUSTOMER", "DATE & TIME", "ITEMS", "TOTAL", "STATUS"]
        
        table_frame = tk.Frame(self.main_area, bg=CARD_COLOR, padx=20, pady=20)
        table_frame.pack(fill="both", expand=True)

        # Header Row
        header_row = tk.Frame(table_frame, bg=CARD_COLOR)
        header_row.pack(fill="x", pady=(0, 10))
        for col in headers:
            tk.Label(header_row, text=col, font=("Segoe UI", 10, "bold"), 
                     bg=CARD_COLOR, fg="#FFAAAA", width=15, anchor="w").pack(side="left", fill="x", expand=True)

        # Separator
        tk.Frame(table_frame, bg="#883333", height=2).pack(fill="x", pady=(0, 10))

        # Dummy Data Rows
        data = [
            ("ORD-1001", "John Doe", "Oct 26, 18:30", "Burger, Salad", "$34.50", "Completed"),
            ("ORD-1002", "Marin Lamern", "Oct 26, 18:35", "Steak, Wine", "$85.00", "Completed"),
            ("ORD-1003", "David Finag", "Oct 26, 18:40", "Pizza, Coke", "$22.00", "Completed"),
            ("ORD-1004", "Dave Wilson", "Oct 26, 18:45", "Pasta", "$18.00", "Completed"),
        ]

        for row in data:
            row_frame = tk.Frame(table_frame, bg=CARD_COLOR)
            row_frame.pack(fill="x", pady=5)
            for item in row:
                tk.Label(row_frame, text=item, font=("Segoe UI", 10), 
                         bg=CARD_COLOR, fg="white", width=15, anchor="w").pack(side="left", fill="x", expand=True)
            
            # Thin separator line
            tk.Frame(table_frame, bg="#441111", height=1).pack(fill="x", pady=2)

# --- TEST BLOCK ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AdminDashboard()
    root.mainloop()