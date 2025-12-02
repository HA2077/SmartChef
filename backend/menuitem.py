class menu_item:
    def __init__(self, id, name, category, price):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
    
    def set_price(self, price):
        if price < 0:
            return "Error: Price cannot be negative"
        self.price = price
    
    def set_name(self, name):
        if not name or not isinstance(name, str):
            return "Error: Name must be a non-empty string"
        self.name = name
    
    def set_category(self, category):
        if not category or not isinstance(category, str):
           return "Error: Category must be a non-empty string"
        self.category = category
    
    def str(self):
        return f"{self.name} ({self.category}) - ${self.price:.2f}"