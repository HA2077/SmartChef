import tkinter as tk
from tkinter import messagebox 
from PIL import Image, ImageTk 
import os
import sys
from gui.loginpage import open_login_window
from gui.pospage import POSDashboard
from gui.kitchenpage import KitchenDashboard
from gui.adminpage import AdminDashboard
from backend.order import clear_all_orders

THEME_COLOR = "#800000" 
TEXT_COLOR = "#FFFFFF" 
FONT_HEADER = ("Segoe UI", 42, "bold")
FONT_SUB = ("Segoe UI", 16)
FONT_CARD_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN = ("Segoe UI", 11, "bold")

class SmartChefApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("SmartChef System")
        self.resizable(True, True)
        self.minsize(1000, 700)
        
        try:
            self.state('zoomed') 
        except:
            self.geometry("1280x800")
            
        # Bind the window close event to the cleanup function
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.dashboards = {}
        self.preload_dashboards()

        self.canvas = tk.Canvas(self, bg=THEME_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.bg_image_id = None
        self.title_id = None
        self.subtitle_id = None
        self.bg_image_original = None
        self.bg_photo = None
        self.load_background()
        
        self.title_id = self.canvas.create_text(0, 0, text="Welcome to SmartChef", 
                                                font=FONT_HEADER, fill=TEXT_COLOR, anchor="center")
        
        self.subtitle_id = self.canvas.create_text(0, 0, text="Select your role to continue", 
                                                   font=FONT_SUB, fill="#DDDDDD", anchor="center")

        self.card_manager = self.create_card_frame("Manager", "assets/Manager.png")
        self.card_waiter = self.create_card_frame("Waiter", "assets/Waiter.png")
        self.card_chef = self.create_card_frame("Chef", "assets/Chef.png")
        self.bind("<Configure>", self.resize_layout)

    def on_closing(self):
        try:
            print("Cleaning up orders...")
            clear_all_orders()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            self.destroy()

    def preload_dashboards(self):
        print("Preloading dashboards...")
        
        # 1. Waiter / POS
        pos = POSDashboard(self)
        pos.withdraw()
        pos.protocol("WM_DELETE_WINDOW", lambda: self.hide_dashboard(pos))
        self.dashboards["Waiter"] = pos
        
        # 2. Chef / Kitchen
        kitchen = KitchenDashboard(self)
        kitchen.withdraw()
        kitchen.protocol("WM_DELETE_WINDOW", lambda: self.hide_dashboard(kitchen))
        self.dashboards["Chef"] = kitchen
        
        # 3. Manager / Admin
        admin = AdminDashboard(self)
        admin.withdraw()
        admin.protocol("WM_DELETE_WINDOW", lambda: self.hide_dashboard(admin))
        self.dashboards["Manager"] = admin

    def hide_dashboard(self, window):
        window.withdraw()
        self.deiconify()
        self.state('zoomed')

    def load_background(self):
        bg_path = "assets/BG.jpg"
        if os.path.exists(bg_path):
            try:
                self.bg_image_original = Image.open(bg_path)
            except Exception as e:
                print(f"Error loading background: {e}")

    def resize_layout(self, event):
        w = self.winfo_width()
        h = self.winfo_height()
        
        if w < 100 or h < 100: return
        if self.bg_image_original:
            resized = self.bg_image_original.resize((w, h), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            
            if self.bg_image_id:
                self.canvas.itemconfig(self.bg_image_id, image=self.bg_photo)
            else:
                self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                self.canvas.tag_lower(self.bg_image_id)

        self.canvas.coords(self.title_id, w/2, h * 0.15)
        self.canvas.coords(self.subtitle_id, w/2, h * 0.22)
        card_y = h * 0.60 
        self.card_manager.place(x=w*0.25, y=card_y, anchor="center", width=280, height=380)
        self.card_waiter.place(x=w*0.50, y=card_y, anchor="center", width=280, height=380)
        self.card_chef.place(x=w*0.75, y=card_y, anchor="center", width=280, height=380)

    def create_card_frame(self, role, icon_path):
        card = tk.Frame(self, bg="white", padx=20, pady=30, relief="raised", bd=2)
        
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                icon_lbl = tk.Label(card, image=photo, bg="white")
                icon_lbl.image = photo 
                icon_lbl.pack(pady=(10, 20))
            except:
                tk.Label(card, text=role[0], font=("Segoe UI", 60), bg="white").pack(pady=20)
        else:
            tk.Label(card, text=role[0], font=("Segoe UI", 60, "bold"), 
                     bg="white", fg=THEME_COLOR).pack(pady=(10, 20))
            
        tk.Label(card, text=role, font=FONT_CARD_TITLE, bg="white", fg="#333").pack(pady=(0, 5))
        tk.Frame(card, bg=THEME_COLOR, height=3, width=60).pack(pady=(0, 25))
        btn = tk.Button(card, text="LOGIN", font=FONT_BTN,
                        bg=THEME_COLOR, fg="white", 
                        activebackground="#A52A2A", activeforeground="white",
                        relief="flat", cursor="hand2", width=18, pady=8,
                        command=lambda: self.open_login(role))
        btn.pack(side="bottom", pady=10)

        btn.bind("<Enter>", lambda e: btn.config(bg="#A52A2A"))
        btn.bind("<Leave>", lambda e: btn.config(bg=THEME_COLOR))
        
        return card

    def open_login(self, role):
        target_dashboard = self.dashboards.get(role)
        open_login_window(self, role, target_dashboard)

if __name__ == "__main__":
    app = SmartChefApp()
    app.mainloop()