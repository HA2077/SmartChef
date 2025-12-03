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
    
    def __str__(self):
        return f"{self.name} ({self.category}) - ${self.price:.2f}"