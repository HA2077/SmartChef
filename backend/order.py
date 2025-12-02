# Order Classes
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import json


class OrderItem:
    """Represents a single item in an order"""
    
    def __init__(self, product_id: str, name: str, price: float, quantity: int = 1):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this item"""
        return self.price * self.quantity
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary"""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'subtotal': self.subtotal
        }
    
    def __str__(self) -> str:
        return f"{self.name} x{self.quantity} @ ${self.price:.2f} = ${self.subtotal:.2f}"


class Order:
    """
    Order class with items list + status
    Manages the complete order flow
    """
    
    # Order status constants
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    
    def __init__(self, customer_id: str, order_id: Optional[str] = None):
        """
        Initialize a new order
        
        Args:
            customer_id: ID of the customer
            order_id: Optional custom order ID (auto-generated if not provided)
        """
        self.order_id = order_id or f"ORD-{uuid.uuid4().hex[:8].upper()}"
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = self.DRAFT
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        
        print(f"✅ Order {self.order_id} created for customer {customer_id}")
    
    def add_item(self, product_id: str, name: str, price: float, quantity: int = 1) -> bool:
        """
        Add an item to the order
        
        Args:
            product_id: Unique product identifier
            name: Product name
            price: Unit price
            quantity: Number of units
            
        Returns:
            bool: True if item was added/updated successfully
        """
        if quantity <= 0:
            print(f"❌ Quantity must be positive")
            return False
        
        # Check if item already exists in order
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                self.updated_at = datetime.now()
                print(f"📦 Updated {item.name}: +{quantity} (Total: {item.quantity})")
                return True
        
        # Add new item
        new_item = OrderItem(product_id, name, price, quantity)
        self.items.append(new_item)
        self.updated_at = datetime.now()
        print(f"✅ Added {quantity} x {name} to order")
        return True
    
    def remove_item(self, product_id: str, quantity: Optional[int] = None) -> bool:
        """
        Remove an item from the order or reduce its quantity
        
        Args:
            product_id: ID of product to remove
            quantity: Specific quantity to remove (None = remove all)
            
        Returns:
            bool: True if item was removed/reduced
        """
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                if quantity is None or quantity >= item.quantity:
                    # Remove entire item
                    removed_item = self.items.pop(i)
                    self.updated_at = datetime.now()
                    print(f"❌ Removed {removed_item.name} from order")
                    return True
                else:
                    # Reduce quantity
                    item.quantity -= quantity
                    self.updated_at = datetime.now()
                    print(f"➖ Reduced {item.name} by {quantity} (Remaining: {item.quantity})")
                    return True
        
        print(f"⚠️ Product {product_id} not found in order")
        return False
    
    def get_total(self) -> float:
        """
        Calculate total cost of all items in the order
        
        Returns:
            float: Total order amount
        """
        return sum(item.subtotal for item in self.items)
    
    def update_status(self, new_status: str) -> bool:
        """
        Update the order status
        
        Args:
            new_status: New status to set
            
        Returns:
            bool: True if status was updated successfully
        """
        valid_statuses = [
            self.DRAFT, self.PENDING, self.PROCESSING,
            self.COMPLETED, self.CANCELLED
        ]
        
        if new_status not in valid_statuses:
            print(f"❌ Invalid status: {new_status}")
            return False
        
        # Check business rules
        if new_status == self.PENDING and not self.items:
            print("❌ Cannot submit empty order")
            return False
        
        if new_status == self.COMPLETED and self.status != self.PROCESSING:
            print("❌ Can only complete orders that are processing")
            return False
        
        # Update status
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        print(f"🔄 Order {self.order_id}: {old_status} → {new_status}")
        return True
    
    def get_item_count(self) -> int:
        """
        Get total number of items (sum of quantities)
        
        Returns:
            int: Total item count
        """
        return sum(item.quantity for item in self.items)
    
    def get_unique_item_count(self) -> int:
        """
        Get count of unique products in the order
        
        Returns:
            int: Number of unique products
        """
        return len(self.items)
    
    def clear_order(self) -> None:
        """Remove all items from the order"""
        self.items.clear()
        self.updated_at = datetime.now()
        print("🧹 All items removed from order")
    
    def display_order(self) -> None:
        """Display formatted order information"""
        print("\n" + "=" * 50)
        print(f"ORDER #{self.order_id}")
        print("=" * 50)
        print(f"Customer: {self.customer_id}")
        print(f"Status: {self.status}")
        print(f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 50)
        
        if not self.items:
            print("No items in order")
        else:
            print("ITEMS:")
            for i, item in enumerate(self.items, 1):
                print(f"{i}. {item.name:<20} x{item.quantity:<3} ${item.price:>6.2f} = ${item.subtotal:>7.2f}")
        
        print("-" * 50)
        print(f"TOTAL: ${self.get_total():>10.2f}")
        print(f"Items: {self.get_item_count()} (Unique: {self.get_unique_item_count()})")
        print("=" * 50)
    
    def to_dict(self) -> Dict:
        """Convert order to dictionary for serialization"""
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'total': self.get_total(),
            'item_count': self.get_item_count(),
            'unique_item_count': self.get_unique_item_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def save_to_file(self, filename: str = None) -> bool:
        """
        Save order to JSON file
        
        Args:
            filename: Optional filename (default: order_{order_id}.json)
            
        Returns:
            bool: True if saved successfully
        """
        if filename is None:
            filename = f"order_{self.order_id}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            print(f"💾 Order saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving order: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filename: str):
        """
        Load order from JSON file
        
        Args:
            filename: JSON file to load from
            
        Returns:
            Order: Loaded Order object or None if failed
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Create order
            order = cls(
                customer_id=data['customer_id'],
                order_id=data['order_id']
            )
            
            # Restore items
            order.items = [
                OrderItem(
                    product_id=item['product_id'],
                    name=item['name'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                for item in data['items']
            ]
            
            # Restore status and timestamps
            order.status = data['status']
            order.created_at = datetime.fromisoformat(data['created_at'])
            order.updated_at = datetime.fromisoformat(data['updated_at'])
            
            print(f"📂 Order loaded from {filename}")
            return order
            
        except Exception as e:
            print(f"❌ Error loading order: {e}")
            return None






