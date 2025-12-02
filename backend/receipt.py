# DONT Focus ON THAT RNfrom datetime import datetime
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import json


class Receipt:
    """
    Receipt class for generating formal receipts from Orders
    Supports multiple receipt types and formatting
    """
    
    # Receipt type constants
    SIMPLE = "SIMPLE"
    DETAILED = "DETAILED"
    TAX_INVOICE = "TAX_INVOICE"
    
    def __init__(self, order, receipt_id: Optional[str] = None, 
                 tax_rate: float = 0.08, tip_percent: float = 0.0):
        """
        Initialize a receipt for an order
        
        Args:
            order: Order object
            receipt_id: Optional receipt ID (auto-generated if not provided)
            tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
            tip_percent: Tip percentage as decimal (e.g., 0.15 for 15%)
        """
        if not order.items:
            raise ValueError("Cannot create receipt for empty order")
        
        self.receipt_id = receipt_id or f"RCP-{uuid.uuid4().hex[:8].upper()}"
        self.order = order
        self.tax_rate = tax_rate
        self.tip_percent = tip_percent
        self.issued_at = datetime.now()
        
        print(f"🧾 Receipt {self.receipt_id} created for Order {order.order_id}")
    
    def calculate_subtotal(self) -> float:
        """Calculate subtotal (before tax and tip)"""
        return self.order.get_total()
    
    def calculate_tax(self) -> float:
        """Calculate tax amount"""
        return self.calculate_subtotal() * self.tax_rate
    
    def calculate_tip(self) -> float:
        """Calculate tip amount"""
        return self.calculate_subtotal() * self.tip_percent
    
    def calculate_total(self) -> float:
        """Calculate total amount (subtotal + tax + tip)"""
        subtotal = self.calculate_subtotal()
        tax = self.calculate_tax()
        tip = self.calculate_tip()
        return subtotal + tax + tip
    
    def generate_simple_receipt(self) -> str:
        """Generate a simple receipt string"""
        receipt_lines = []
        receipt_lines.append(f"RECEIPT #{self.receipt_id}")
        receipt_lines.append(f"Order: #{self.order.order_id}")
        receipt_lines.append(f"Date: {self.issued_at.strftime('%Y-%m-%d %H:%M')}")
        receipt_lines.append("-" * 40)
        
        for item in self.order.items:
            receipt_lines.append(f"{item.name} x{item.quantity} = ${item.subtotal:.2f}")
        
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"Subtotal: ${self.calculate_subtotal():.2f}")
        receipt_lines.append(f"Tax ({self.tax_rate*100:.1f}%): ${self.calculate_tax():.2f}")
        
        if self.tip_percent > 0:
            receipt_lines.append(f"Tip ({self.tip_percent*100:.1f}%): ${self.calculate_tip():.2f}")
        
        receipt_lines.append(f"TOTAL: ${self.calculate_total():.2f}")
        receipt_lines.append("=" * 40)
        receipt_lines.append("Thank you for your business!")
        
        return "\n".join(receipt_lines)
    
    def generate_detailed_receipt(self) -> str:
        """Generate a detailed receipt with item breakdown"""
        receipt_lines = []
        receipt_lines.append(" " * 15 + "INVOICE / RECEIPT")
        receipt_lines.append("=" * 50)
        receipt_lines.append(f"Receipt: #{self.receipt_id:<20} Order: #{self.order.order_id}")
        receipt_lines.append(f"Customer: {self.order.customer_id}")
        receipt_lines.append(f"Date: {self.issued_at.strftime('%Y-%m-%d %I:%M %p')}")
        receipt_lines.append("=" * 50)
        
        # Header
        receipt_lines.append(f"{'Item':<20} {'Qty':>5} {'Price':>8} {'Total':>10}")
        receipt_lines.append("-" * 50)
        
        # Items
        for item in self.order.items:
            receipt_lines.append(
                f"{item.name[:19]:<20} "
                f"{item.quantity:>5} "
                f"${item.price:>7.2f} "
                f"${item.subtotal:>9.2f}"
            )
        
        receipt_lines.append("-" * 50)
        
        # Summary
        subtotal = self.calculate_subtotal()
        tax = self.calculate_tax()
        tip = self.calculate_tip()
        total = self.calculate_total()
        
        receipt_lines.append(f"{'Subtotal:':<35} ${subtotal:>10.2f}")
        receipt_lines.append(f"{'Tax (' + f'{self.tax_rate*100:.1f}%' + '):':<35} ${tax:>10.2f}")
        
        if self.tip_percent > 0:
            receipt_lines.append(f"{'Tip (' + f'{self.tip_percent*100:.1f}%' + '):':<35} ${tip:>10.2f}")
        
        receipt_lines.append("=" * 50)
        receipt_lines.append(f"{'GRAND TOTAL:':<35} ${total:>10.2f}")
        receipt_lines.append("=" * 50)
        
        # Footer
        receipt_lines.append(f"Items: {self.order.get_item_count()} | "
                           f"Unique: {self.order.get_unique_item_count()}")
        receipt_lines.append("Order Status: " + self.order.status)
        receipt_lines.append("\nThank you for your purchase!")
        receipt_lines.append("Please retain this receipt for your records")
        
        return "\n".join(receipt_lines)
    
    def print_receipt(self, receipt_type: str = SIMPLE) -> None:
        """
        Print receipt to console
        
        Args:
            receipt_type: Type of receipt to print (SIMPLE or DETAILED)
        """
        if receipt_type == self.SIMPLE:
            receipt_text = self.generate_simple_receipt()
        elif receipt_type == self.DETAILED:
            receipt_text = self.generate_detailed_receipt()
        else:
            raise ValueError(f"Invalid receipt type: {receipt_type}")
        
        print("\n" + receipt_text)
    
    def save_receipt(self, filename: Optional[str] = None, 
                    receipt_type: str = SIMPLE) -> bool:
        """
        Save receipt to text file
        
        Args:
            filename: Optional filename (default: receipt_{receipt_id}.txt)
            receipt_type: Type of receipt to save
            
        Returns:
            bool: True if saved successfully
        """
        if receipt_type == self.SIMPLE:
            receipt_text = self.generate_simple_receipt()
        elif receipt_type == self.DETAILED:
            receipt_text = self.generate_detailed_receipt()
        else:
            raise ValueError(f"Invalid receipt type: {receipt_type}")
        
        if filename is None:
            filename = f"receipt_{self.receipt_id}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(receipt_text)
            print(f"💾 Receipt saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving receipt: {e}")
            return False
    
    def to_dict(self) -> Dict:
        """Convert receipt to dictionary for serialization"""
        return {
            'receipt_id': self.receipt_id,
            'order_id': self.order.order_id,
            'customer_id': self.order.customer_id,
            'issued_at': self.issued_at.isoformat(),
            'tax_rate': self.tax_rate,
            'tip_percent': self.tip_percent,
            'subtotal': self.calculate_subtotal(),
            'tax': self.calculate_tax(),
            'tip': self.calculate_tip(),
            'total': self.calculate_total(),
            'item_count': self.order.get_item_count()
        }
    
    def to_json(self) -> str:
        """Convert receipt to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class DigitalReceipt(Receipt):
    """
    Enhanced receipt for digital delivery with additional features
    """
    
    def __init__(self, order, email: str, receipt_id: Optional[str] = None,
                 tax_rate: float = 0.08, tip_percent: float = 0.0):
        """
        Initialize digital receipt with email delivery
        
        Args:
            order: Order object
            email: Customer email for delivery
            receipt_id: Optional receipt ID
            tax_rate: Tax rate as decimal
            tip_percent: Tip percentage as decimal
        """
        super().__init__(order, receipt_id, tax_rate, tip_percent)
        self.email = email
        self.delivery_status = "PENDING"
        self.delivered_at = None
    
    def send_receipt(self) -> bool:
        """
        Simulate sending receipt via email
        
        Returns:
            bool: True if "sent" successfully
        """
        try:
            # In real implementation, this would send actual email
            self.delivery_status = "SENT"
            self.delivered_at = datetime.now()
            print(f"📧 Receipt sent to {self.email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send receipt: {e}")
            return False
    
    def generate_html_receipt(self) -> str:
        """Generate HTML formatted receipt for email"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                .details {{ margin: 20px 0; }}
                .items {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .items th, .items td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .items th {{ background-color: #f2f2f2; }}
                .total {{ font-size: 18px; font-weight: bold; margin-top: 20px; }}
                .footer {{ margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>INVOICE / RECEIPT</h1>
                <p>Receipt: #{self.receipt_id} | Order: #{self.order.order_id}</p>
            </div>
            
            <div class="details">
                <p><strong>Customer:</strong> {self.order.customer_id}</p>
                <p><strong>Email:</strong> {self.email}</p>
                <p><strong>Date:</strong> {self.issued_at.strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <table class="items">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in self.order.items:
            html += f"""
                    <tr>
                        <td>{item.name}</td>
                        <td>{item.quantity}</td>
                        <td>${item.price:.2f}</td>
                        <td>${item.subtotal:.2f}</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
            </table>
            
            <div class="total">
                <p>Subtotal: ${self.calculate_subtotal():.2f}</p>
                <p>Tax ({self.tax_rate*100:.1f}%): ${self.calculate_tax():.2f}</p>
        """
        
        if self.tip_percent > 0:
            html += f'<p>Tip ({self.tip_percent*100:.1f}%): ${self.calculate_tip():.2f}</p>'
        
        html += f"""
                <p><strong>GRAND TOTAL: ${self.calculate_total():.2f}</strong></p>
            </div>
            
            <div class="footer">
                <p>This is a digital receipt. Please retain for your records.</p>
                <p>Order Status: {self.order.status}</p>
                <p>Thank you for your business!</p>
            </div>
        </body>
        </html>
        """
        
        return html


class ReceiptManager:
    """
    Manager class for handling multiple receipts
    """
    
    def __init__(self):
        self.receipts = {}
    
    def create_receipt(self, order, receipt_type: str = "standard", **kwargs) -> Receipt:
        """
        Create a receipt for an order
        
        Args:
            order: Order object
            receipt_type: Type of receipt ("standard" or "digital")
            **kwargs: Additional arguments for receipt constructor
            
        Returns:
            Receipt: Created receipt object
        """
        if receipt_type.lower() == "digital":
            if "email" not in kwargs:
                raise ValueError("Digital receipt requires email address")
            receipt = DigitalReceipt(order, **kwargs)
        else:
            receipt = Receipt(order, **kwargs)
        
        self.receipts[receipt.receipt_id] = receipt
        return receipt
    
    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        """Retrieve receipt by ID"""
        return self.receipts.get(receipt_id)
    
    def get_all_receipts(self) -> List[Receipt]:
        """Get all receipts"""
        return list(self.receipts.values())
    
    def get_total_revenue(self) -> float:
        """Calculate total revenue from all receipts"""
        return sum(receipt.calculate_total() for receipt in self.receipts.values())
    
    def save_all_receipts(self, filename: str = "all_receipts.json") -> bool:
        """Save all receipts to JSON file"""
        try:
            receipts_data = {
                'receipts': [receipt.to_dict() for receipt in self.receipts.values()],
                'total_count': len(self.receipts),
                'total_revenue': self.get_total_revenue(),
                'exported_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(receipts_data, f, indent=2)
            
            print(f"💾 All receipts saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving receipts: {e}")
            return False


