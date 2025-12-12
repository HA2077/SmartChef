import tkinter as tk
from tkinter import messagebox 
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

        # 1. LOAD APP ICON
        icon_path = ("assets/SC.png") 
        if os.path.exists(icon_path):
            try:
                icon_img = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon_img)
            except Exception as e:
                print(f"Error loading app icon: {e}")
        
        self.maximize_me()
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.dashboards = {}
        self.preload_dashboards()

        self.canvas = tk.Canvas(self, bg=THEME_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 2. LOAD BACKGROUND
        self.bg_image_obj = None
        self.bg_id = None
        self.load_background()
        
        self.title_id = self.canvas.create_text(0, 0, text="Welcome to SmartChef", 
                                                font=FONT_HEADER, fill=TEXT_COLOR, anchor="center")
        
        self.subtitle_id = self.canvas.create_text(0, 0, text="Select your role to continue", 
                                                   font=FONT_SUB, fill="#DDDDDD", anchor="center")

        self.card_manager = self.create_card_frame("Manager", "assets/Manager.png", scale=4)
        self.card_waiter = self.create_card_frame("Waiter", "assets/Waiter.png", scale=4)
        self.card_chef = self.create_card_frame("Chef", "assets/Chef.png", scale=2)
        
        self.bind("<Configure>", self.resize_layout)

    def maximize_me(self):
        try:
            self.state('zoomed') 
            return
        except tk.TclError:
            pass
        try:
            self.attributes('-zoomed', True)
            return
        except tk.TclError:
            pass
        try:
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")
        except:
            self.geometry("1280x800")

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
        pos = POSDashboard(self)
        pos.withdraw()
        pos.protocol("WM_DELETE_WINDOW", lambda: self.hide_dashboard(pos))
        self.dashboards["Waiter"] = pos
        
        kitchen = KitchenDashboard(self)
        kitchen.withdraw()
        kitchen.protocol("WM_DELETE_WINDOW", lambda: self.hide_dashboard(kitchen))
        self.dashboards["Chef"] = kitchen
        
        admin = AdminDashboard(self)
        admin.withdraw()
        admin.protocol("WM_DELETE_WINDOW", lambda: self.hide_dashboard(admin))
        self.dashboards["Manager"] = admin

    def hide_dashboard(self, window):
        window.withdraw()
        self.lift()
        self.focus_force()

    def load_background(self):
        bg_path = ("assets/BG.png")
        if os.path.exists(bg_path):
            try:
                self.bg_image_obj = tk.PhotoImage(file=bg_path)
                self.bg_id = self.canvas.create_image(0, 0, image=self.bg_image_obj, anchor="nw")
                self.canvas.tag_lower(self.bg_id)
            except Exception as e:
                print(f"Error loading background: {e}")

    def resize_layout(self, event):
        w = self.winfo_width()
        h = self.winfo_height()
        
        self.canvas.coords(self.title_id, w/2, h * 0.15)
        self.canvas.coords(self.subtitle_id, w/2, h * 0.22)
        
        card_y = h * 0.60 
        
        col_1 = w * 0.25
        col_2 = w * 0.50
        col_3 = w * 0.75
        
        self.card_manager.place(x=col_1, y=card_y, anchor="center", width=280, height=380)
        self.card_waiter.place(x=col_2, y=card_y, anchor="center", width=280, height=380)
        self.card_chef.place(x=col_3, y=card_y, anchor="center", width=280, height=380)

    def create_card_frame(self, role, relative_icon_path, scale=4):
        card = tk.Frame(self, bg="white", padx=20, pady=30, relief="raised", bd=2)
        
        full_path = (relative_icon_path)
        
        if os.path.exists(full_path):
            try:
                original_image = tk.PhotoImage(file=full_path)
                photo = original_image.subsample(scale, scale) 
                
                if not hasattr(self, "card_icons"):
                    self.card_icons = []
                self.card_icons.append(photo)
                self.card_icons.append(original_image)
                
                icon_lbl = tk.Label(card, image=photo, bg="white")
                icon_lbl.pack(pady=(10, 20))
            except Exception as e:
                print(f"Image load error for {role}: {e}")
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
        
        if target_dashboard.state() != "withdrawn":
            target_dashboard.lift()
            target_dashboard.focus_force()

if __name__ == "__main__":
    app = SmartChefApp()
    app.mainloop()