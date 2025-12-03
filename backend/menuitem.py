import json
import os

class MenuItem:
    def __init__(self, id: str, name: str, category: str, price: float):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
    
    def set_price(self, price: float):
        if price < 0:
            return "Error: Price cannot be negative"
        self.price = price
    
    def set_name(self, name: str):
        if not name or not isinstance(name, str):
            return "Error: Name must be a non-empty string"
        self.name = name
    
    def set_category(self, category: str):
        if not category or not isinstance(category, str):
           return "Error: Category must be a non-empty string"
        self.category = category
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["name"], data["category"], data["price"])
    
    def __str__(self):
        return f"{self.name} ({self.category}) - ${self.price:.2f}"

def save_menu_items(items, filename="data/menu.json"):
    if not os.path.exists("data"):
        os.makedirs("data")
    
    try:
        with open(filename, 'w') as f:
            json.dump([item.to_dict() for item in items], f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving menu: {e}")
        return False

def load_menu_items(filename="data/menu.json"):
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return [MenuItem.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []