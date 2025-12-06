import tkinter as tk

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

        # Header
        header = tk.Frame(self, bg=BG_COLOR, height=60)
        header.pack(fill="x", padx=20, pady=10)
        tk.Label(header, text="Kitchen Display - Active Orders", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg="#999").pack(anchor="w")

        # Scrollable Area (Simplified as a grid frame for demo)
        self.grid_frame = tk.Frame(self, bg=BG_COLOR)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create dummy tickets
        self.create_ticket(0, 0, "TABLE 4", "14:35", "Pending")
        self.create_ticket(0, 1, "TABLE 12", "05:20", "Preparing")
        self.create_ticket(0, 2, "TABLE 7", "READY", "Ready")
        self.create_ticket(0, 3, "TABLE 6", "15:35", "Preparing")
        
        self.create_ticket(1, 0, "TABLE 9", "05:20", "Pending")
        self.create_ticket(1, 1, "TABLE 3", "05:20", "Preparing")
        self.create_ticket(1, 2, "TABLE 1", "22:10", "Ready")
        self.create_ticket(1, 3, "TABLE 15", "22:10", "Ready")

    def create_ticket(self, row, col, table_name, time_val, status):
        # Border Frame (Simulates the glow)
        border_color = "white"
        if status == "Pending": border_color = STATUS_PENDING
        elif status == "Preparing": border_color = STATUS_PREP
        elif status == "Ready": border_color = STATUS_READY

        container = tk.Frame(self.grid_frame, bg=border_color, padx=2, pady=2)
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Inner Card
        card = tk.Frame(container, bg=CARD_COLOR, width=280, height=220)
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)

        # Header
        tk.Label(card, text="Order Ticket", font=("Segoe UI", 9), bg=CARD_COLOR, fg="#CCC").place(x=15, y=10)
        tk.Label(card, text="ⓘ", font=("Segoe UI", 12), bg=CARD_COLOR, fg="#CCC").place(x=250, y=10)

        # Table Name
        tk.Label(card, text=table_name, font=("Segoe UI", 24, "bold"), bg=CARD_COLOR, fg="white").place(x=15, y=30)

        # Items
        items = "2x Spicy Burger\n1x Cobb Salad\n1x Iced Tea\n1x Choco Lava Cake"
        tk.Label(card, text=items, font=("Segoe UI", 10), bg=CARD_COLOR, fg="#EEE", justify="left").place(x=15, y=80)

        # Timer
        tk.Label(card, text=time_val, font=("Segoe UI", 18, "bold"), bg=CARD_COLOR, fg="white").place(x=200, y=85)

        # Status Pill
        btn_bg = border_color
        status_lbl = tk.Label(card, text=status, font=("Segoe UI", 10, "bold"), 
                              bg=btn_bg, fg="black" if status=="Pending" else "white", width=15, pady=5)
        status_lbl.place(x=80, y=170)

        # Configure grid weights
        self.grid_frame.columnconfigure(col, weight=1)
        self.grid_frame.rowconfigure(row, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = KitchenDashboard()
    root.mainloop()