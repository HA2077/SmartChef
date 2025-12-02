class MenuItem: # Renamed class to MenuItem
    def __init__(self, id: str, name: str, category: str, price: float): # Added type hints
        self.id = id
        self.name = name
        self.category = category
        self.price = price
    
    def set_price(self, price: float): # Added type hint
        if price < 0:
            return "Error: Price cannot be negative"
        self.price = price
    
    def set_name(self, name: str): # Added type hint
        if not name or not isinstance(name, str):
            return "Error: Name must be a non-empty string"
        self.name = name
    
    def set_category(self, category: str): # Added type hint
        if not category or not isinstance(category, str):
           return "Error: Category must be a non-empty string"
        self.category = category
    
    def __str__(self): # Renamed str to __str__
        return f"{self.name} ({self.category}) - ${self.price:.2f}"