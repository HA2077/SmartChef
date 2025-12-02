# Order Classes
from datetime import datetime
from typing import List, Dict
import uuid


class OrderItem:
    """Represents a single item in an order"""
    
    def __init__(self, product_id: str, name: str, price: float, quantity: int = 1):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
    
    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class Order:
    """Order class with items list + status"""
    
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    
    def __init__(self, customer_id: str, order_id: str = None):
        self.order_id = order_id or f"ORD-{uuid.uuid4().hex[:8].upper()}"
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = self.DRAFT
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    def add_item(self, product_id: str, name: str, price: float, quantity: int = 1) -> bool:
        if quantity <= 0:
            return False
        
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                self.updated_at = datetime.now()
                return True
        
        new_item = OrderItem(product_id, name, price, quantity)
        self.items.append(new_item)
        self.updated_at = datetime.now()
        return True
    
    def remove_item(self, product_id: str, quantity: int = None) -> bool:
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                if quantity is None or quantity >= item.quantity:
                    self.items.pop(i)
                    self.updated_at = datetime.now()
                    return True
                else:
                    item.quantity -= quantity
                    self.updated_at = datetime.now()
                    return True
        
        return False
    
    def get_total(self) -> float:
        return sum(item.subtotal for item in self.items)
    
    def update_status(self, new_status: str) -> bool:
        valid_statuses = [
            self.DRAFT, self.PENDING, self.PROCESSING,
            self.COMPLETED, self.CANCELLED
        ]
        
        if new_status not in valid_statuses:
            return False
        
        if new_status == self.PENDING and not self.items:
            return False
        
        if new_status == self.COMPLETED and self.status != self.PROCESSING:
            return False
        
        self.status = new_status
        self.updated_at = datetime.now()
        return True
    
    def clear_order(self) -> None:
        self.items.clear()
        self.updated_at = datetime.now()






