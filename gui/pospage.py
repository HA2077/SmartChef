import tkinter as tk

BG_COLOR = "#2B0505"        # Main Background
SECTION_BG = "#550a0a"      # Lighter sections
BTN_RED = "#AA3333"         # Buttons
TEXT_WHITE = "#FFFFFF"

class POSDashboard(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("SmartChef - POS")
        self.geometry("1200x700")
        self.configure(bg=BG_COLOR)
        
        # Main Layout: 3 Columns
        # 1. MENU CATEGORIES (Left)
        self.frame_menu = tk.Frame(self, bg=SECTION_BG, width=300, padx=10, pady=10)
        self.frame_menu.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.frame_menu.pack_propagate(False)
        self.build_menu_section()

        # 2. CURRENT ORDER (Center)
        self.frame_order = tk.Frame(self, bg=SECTION_BG, width=400, padx=10, pady=10)
        self.frame_order.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        self.build_order_section()

        # 3. CHECKOUT (Right)
        self.frame_checkout = tk.Frame(self, bg=SECTION_BG, width=300, padx=20, pady=20)
        self.frame_checkout.pack(side="right", fill="y", padx=(5, 10), pady=10)
        self.frame_checkout.pack_propagate(False)
        self.build_checkout_section()

    def build_menu_section(self):
        tk.Label(self.frame_menu, text="MENU", font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(pady=(0, 10))
        
        # Grid of buttons
        categories = [
            "APPETIZERS", "MAIN\nCOURSES", 
            "DESSERTS", "DRINKS", 
            "SIDES", "SPECIALS",
            "SALADS", "PASTA",
            "BURGERS", "PIZZA"
        ]
        
        btn_frame = tk.Frame(self.frame_menu, bg=SECTION_BG)
        btn_frame.pack(fill="both", expand=True)

        for i, cat in enumerate(categories):
            btn = tk.Button(btn_frame, text=cat, bg=BTN_RED, fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", height=3)
            btn.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

    def build_order_section(self):
        tk.Label(self.frame_order, text="CURRENT ORDER", font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(pady=(0, 10))

        # Header for list
        hdr = tk.Frame(self.frame_order, bg=SECTION_BG)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Quantity | Name", bg=SECTION_BG, fg="white", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="Price", bg=SECTION_BG, fg="white", font=("Segoe UI", 10, "bold")).pack(side="right")

        # Scrollable List Placeholder (Using Frame for styling)
        list_area = tk.Frame(self.frame_order, bg=SECTION_BG)
        list_area.pack(fill="both", expand=True, pady=10)
        
        items = [
            ("2x", "Spicy Burger", "$24.00"),
            ("1x", "Cobb Salad", "$12.50"),
            ("3x", "Iced Tea", "$9.00"),
            ("1x", "Choco Lava Cake", "$8.00"),
        ]

        for qty, name, price in items:
            row = tk.Frame(list_area, bg=SECTION_BG)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=f"{qty}   {name}", bg=SECTION_BG, fg="white", font=("Segoe UI", 12)).pack(side="left")
            tk.Label(row, text=price, bg=SECTION_BG, fg="white", font=("Segoe UI", 12)).pack(side="right")

    def build_checkout_section(self):
        tk.Label(self.frame_checkout, text="CHECKOUT", font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(pady=(0, 20))

        # Totals
        self.add_total_row("Subtotal:", "$53.50", 16)
        self.add_total_row("Tax:", "$4.82", 14)
        
        tk.Frame(self.frame_checkout, bg="white", height=2).pack(fill="x", pady=20)
        
        self.add_total_row("Total:", "$58.32", 22, bold=True)

        # Big Button
        btn = tk.Button(self.frame_checkout, text="SEND TO\nKITCHEN", bg="#CC3333", fg="white",
                        font=("Segoe UI", 16, "bold"), relief="flat", height=3, cursor="hand2")
        btn.pack(side="bottom", fill="x", pady=20)

    def add_total_row(self, label, value, size, bold=False):
        font_style = ("Segoe UI", size, "bold" if bold else "normal")
        row = tk.Frame(self.frame_checkout, bg=SECTION_BG)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, bg=SECTION_BG, fg="white", font=font_style).pack(side="left")
        tk.Label(row, text=value, bg=SECTION_BG, fg="white", font=font_style).pack(side="right")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = POSDashboard()
    root.mainloop()