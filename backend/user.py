import json

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def login(self, username, password):
        return self.username == username and self.password == password

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, "admin")

class Waiter(User):
    def __init__(self, username, password):
        super().__init__(username, password, "waiter")

class Chef(User):
    def __init__(self, username, password):
        super().__init__(username, password, "chef")

def save_users(users, filename="data/users.json"):
    with open(filename, 'w') as f:
        json.dump([user.to_dict() for user in users], f, indent=4)

def load_users(filename="data/users.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            users = []
            for user_data in data:
                role = user_data.get("role")
                if role == "admin":
                    user = Admin(user_data["username"], user_data["password"])
                elif role == "waiter":
                    user = Waiter(user_data["username"], user_data["password"])
                elif role == "chef":
                    user = Chef(user_data["username"], user_data["password"])
                else:
                    user = User(user_data["username"], user_data["password"], role)
                users.append(user)
            return users
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
