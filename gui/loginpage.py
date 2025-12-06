import tkinter as tk
from tkinter import messagebox
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.user import load_users, Admin, Waiter, Chef
from .pospage import POSDashboard
from .kitchenpage import KitchenDashboard
from .adminpage import AdminDashboard
COLOR_ACCENT = "#800000"
COLOR_BG = "#FFFFFF"

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, role):
        super().__init__(parent)
        self.role = role
        self.users = load_users()

        self.title(f"{role} Login")
        self.geometry("350x450")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.center_window(350, 450)
        self.build_ui()

    def center_window(self, w, h):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def build_ui(self):
        header = tk.Frame(self, bg=COLOR_ACCENT, height=80)
        header.pack(fill="x")
        
        lbl = tk.Label(header, text=f"{self.role}", font=("Segoe UI", 20, "bold"),
                       bg=COLOR_ACCENT, fg="white")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        form_frame = tk.Frame(self, bg=COLOR_BG, padx=30, pady=30)
        form_frame.pack(expand=True, fill="both")

        tk.Label(form_frame, text="Username", bg=COLOR_BG, fg="#555", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.entry_user = tk.Entry(form_frame, font=("Helvetica", 12), relief="solid", bd=1)
        self.entry_user.pack(fill="x", pady=(5, 15), ipady=3)

        tk.Label(form_frame, text="Password", bg=COLOR_BG, fg="#555", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.entry_pass = tk.Entry(form_frame, font=("Helvetica", 12), relief="solid", bd=1, show="•")
        self.entry_pass.pack(fill="x", pady=(5, 25), ipady=3)

        btn_login = tk.Button(form_frame, text="SIGN IN", bg=COLOR_ACCENT, fg="white",
                              font=("Helvetica", 12, "bold"), relief="flat", cursor="hand2",
                              command=self.handle_login)
        btn_login.pack(fill="x", ipady=8)

    def handle_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        for user in self.users:
            if user.get_username() == username and user.login(username, password):
                role_map = {"Manager": Admin, "Waiter": Waiter, "Chef": Chef}
                target_class = role_map.get(self.role)
                
                if isinstance(user, target_class) or isinstance(user, Admin):
                    # --- START NEW DASHBOARD OPENING LOGIC ---
                    messagebox.showinfo("Success", f"Welcome back, {username}!")
                    
                    if self.role == "Waiter":
                        POSDashboard(self.master)
                    elif self.role == "Chef":
                        KitchenDashboard(self.master)
                    elif self.role == "Manager":
                        AdminDashboard(self.master)
                    
                    self.destroy() # Close the login window
                    # --- END NEW DASHBOARD OPENING LOGIC ---
                    return
                else:
                    messagebox.showerror("Access Denied", f"This account is not a {self.role}.")
                    return
        
        messagebox.showerror("Failed", "Invalid Username or Password")

def open_login_window(parent, role):
    window = LoginWindow(parent, role)
    window.transient(parent)
    window.grab_set()
    parent.wait_window(window)