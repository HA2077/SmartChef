import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.menuitem import load_menu_items
from backend.order import Order

BG_COLOR = "#2B0505"        
SECTION_BG = "#550a0a"     
BTN_RED = "#AA3333"       
TEXT_WHITE = "#FFFFFF"

class POSDashboard(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent) 
        self.title("SmartChef - POS")
        self.geometry("1200x700")
        self.configure(bg=BG_COLOR)

        self.current_order = Order("Walk-in")
        self.menu_items = load_menu_items() 
        self.menu_data = {} 
        self.organize_menu_data()

        self.bg_image_original = None
        self.bg_photo = None
        self.bg_label = tk.Label(self, bg=BG_COLOR)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.load_background()
        
        # --- Main Layout ---
        # 1. MENU SECTION (Left)
        self.frame_menu = tk.Frame(self, bg=SECTION_BG, width=300, padx=10, pady=10)
        self.frame_menu.pack(side="left", fill="y", padx=(20, 5), pady=20)
        self.frame_menu.pack_propagate(False)
        
        self.menu_content_frame = tk.Frame(self.frame_menu, bg=SECTION_BG)
        self.menu_content_frame.pack(fill="both", expand=True)

        self.build_menu_section()

        # 2. CURRENT ORDER (Center)
        self.frame_order = tk.Frame(self, bg=SECTION_BG, width=450, padx=10, pady=10)
        self.frame_order.pack(side="left", fill="both", expand=True, padx=5, pady=20)
        self.build_order_section()

        # 3. CHECKOUT (Right)
        self.frame_checkout = tk.Frame(self, bg=SECTION_BG, width=300, padx=20, pady=20)
        self.frame_checkout.pack(side="right", fill="y", padx=(5, 20), pady=20)
        self.frame_checkout.pack_propagate(False)
        self.build_checkout_section()
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

    def organize_menu_data(self):
        self.menu_data = {}
        if not self.menu_items:
            return
        for item in self.menu_items:
            cat = item.category
            if cat not in self.menu_data:
                self.menu_data[cat] = []
            self.menu_data[cat].append(item)

    # --- Menu Section Logic ---
    def clear_menu_content(self):
        for widget in self.menu_content_frame.winfo_children():
            widget.destroy()

    def build_menu_section(self):
        self.clear_menu_content()
        tk.Label(self.menu_content_frame, text="MENU CATEGORIES", font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(pady=(0, 10))
        
        categories = list(self.menu_data.keys())
        if not categories:
             tk.Label(self.menu_content_frame, text="No Menu Loaded", bg=SECTION_BG, fg="white").pack()
             return

        btn_frame = tk.Frame(self.menu_content_frame, bg=SECTION_BG)
        btn_frame.pack(fill="both", expand=True)

        for i, cat in enumerate(categories):
            command = lambda c=cat: self.show_menu_items(c)
            btn = tk.Button(btn_frame, text=cat, bg=BTN_RED, fg="white", 
                             font=("Segoe UI", 10, "bold"), relief="flat", height=3, command=command)
            btn.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

    def show_menu_items(self, category_name):
        self.clear_menu_content()
        
        header_frame = tk.Frame(self.menu_content_frame, bg=SECTION_BG)
        header_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(header_frame, text="< BACK", bg=BTN_RED, fg="white", 
                  font=("Segoe UI", 10, "bold"), relief="flat", height=1, 
                  command=self.build_menu_section).pack(side="left", padx=(0, 10))
        
        tk.Label(header_frame, text=category_name, font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(side="left", fill="x", expand=True)
        
        item_canvas = tk.Canvas(self.menu_content_frame, bg=SECTION_BG, highlightthickness=0)
        item_scrollbar = tk.Scrollbar(self.menu_content_frame, orient="vertical", command=item_canvas.yview)
        scrollable_frame = tk.Frame(item_canvas, bg=SECTION_BG)
        
        item_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", 
                                   width=self.frame_menu.winfo_width() - 30)

        scrollable_frame.bind("<Configure>", lambda e: item_canvas.configure(scrollregion=item_canvas.bbox("all")))
        item_canvas.configure(yscrollcommand=item_scrollbar.set)
        
        item_scrollbar.pack(side="right", fill="y")
        item_canvas.pack(side="left", fill="both", expand=True)
        
        items = self.menu_data.get(category_name, [])
        for i, item in enumerate(items):
            cmd = lambda it=item: self.add_item_to_order(it)
            item_btn = tk.Button(scrollable_frame, 
                                 text=f"{item.name}\n${item.price}", 
                                 bg=BTN_RED, fg="white", 
                                 font=("Segoe UI", 10, "bold"), relief="flat", height=3, 
                                 command=cmd)
            item_btn.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)

    # --- Order Logic ---
    def add_item_to_order(self, item):
        self.current_order.add_item(item.id, item.name, item.price, 1)
        self.refresh_order_display()

    def cancel_order(self):
        if not self.current_order.items:
            return
        if messagebox.askyesno("Cancel Order", "Are you sure you want to clear the current order?"):
            self.current_order.clear_order()
            self.refresh_order_display()

    def build_order_section(self):
        tk.Label(self.frame_order, text="CURRENT ORDER", font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(pady=(0, 10))

        # Header
        hdr = tk.Frame(self.frame_order, bg=SECTION_BG)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Qty   Item Name", bg=SECTION_BG, fg="white", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="Price", bg=SECTION_BG, fg="white", font=("Segoe UI", 10, "bold")).pack(side="right")

        # Scrollable Order List
        self.order_canvas = tk.Canvas(self.frame_order, bg=SECTION_BG, highlightthickness=0)
        self.order_scroll = tk.Scrollbar(self.frame_order, orient="vertical", command=self.order_canvas.yview)
        self.order_list_frame = tk.Frame(self.order_canvas, bg=SECTION_BG)
        
        self.order_canvas.create_window((0, 0), window=self.order_list_frame, anchor="nw", width=400)
        self.order_list_frame.bind("<Configure>", lambda e: self.order_canvas.configure(scrollregion=self.order_canvas.bbox("all")))
        self.order_canvas.configure(yscrollcommand=self.order_scroll.set)
        
        self.order_scroll.pack(side="right", fill="y")
        self.order_canvas.pack(side="left", fill="both", expand=True)

    def refresh_order_display(self):
        for widget in self.order_list_frame.winfo_children():
            widget.destroy()

        for item in self.current_order.items:
            row = tk.Frame(self.order_list_frame, bg=SECTION_BG)
            row.pack(fill="x", pady=2)
            
            txt_left = f"{item.quantity}x   {item.name}"
            txt_right = f"${item.subtotal:.2f}"
            
            tk.Label(row, text=txt_left, bg=SECTION_BG, fg="white", font=("Segoe UI", 11)).pack(side="left")
            tk.Label(row, text=txt_right, bg=SECTION_BG, fg="white", font=("Segoe UI", 11)).pack(side="right")

        self.update_totals()

    def update_totals(self):
        subtotal = self.current_order.get_total()
        tax = subtotal * 0.08
        total = subtotal + tax
        
        self.lbl_sub_val.config(text=f"${subtotal:.2f}")
        self.lbl_tax_val.config(text=f"${tax:.2f}")
        self.lbl_total_val.config(text=f"${total:.2f}")

    # --- Checkout Section ---
    def build_checkout_section(self):
        tk.Label(self.frame_checkout, text="CHECKOUT", font=("Segoe UI", 14, "bold"), bg=SECTION_BG, fg="white").pack(pady=(0, 20))

        self.lbl_sub_val = self.add_total_row("Subtotal:", "$0.00", 16)
        self.lbl_tax_val = self.add_total_row("Tax (8%):", "$0.00", 14)
        
        tk.Frame(self.frame_checkout, bg="white", height=2).pack(fill="x", pady=20)
        
        self.lbl_total_val = self.add_total_row("Total:", "$0.00", 22, bold=True)

        # Buttons
        # Send to Kitchen (Bottom)
        btn_send = tk.Button(self.frame_checkout, text="SEND TO\nKITCHEN", bg="#CC3333", fg="white",
                         font=("Segoe UI", 16, "bold"), relief="flat", height=3, cursor="hand2",
                         command=lambda: messagebox.showinfo("Order Sent", f"Order #{self.current_order.order_id} sent!"))
        btn_send.pack(side="bottom", fill="x", pady=(10, 0))

        # Cancel Order (Above Send)
        btn_cancel = tk.Button(self.frame_checkout, text="CANCEL ORDER", bg="#FF5555", fg="white",
                         font=("Segoe UI", 12, "bold"), relief="flat", height=2, cursor="hand2",
                         command=self.cancel_order)
        btn_cancel.pack(side="bottom", fill="x", pady=(0, 10))

    def add_total_row(self, label, value, size, bold=False):
        font_style = ("Segoe UI", size, "bold" if bold else "normal")
        row = tk.Frame(self.frame_checkout, bg=SECTION_BG)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, bg=SECTION_BG, fg="white", font=font_style).pack(side="left")
        lbl_val = tk.Label(row, text=value, bg=SECTION_BG, fg="white", font=font_style)
        lbl_val.pack(side="right")
        return lbl_val

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = POSDashboard() 
    root.mainloop()