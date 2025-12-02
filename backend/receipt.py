# DONT Focus ON THAT RNfrom datetime import datetime
from datetime import datetime
from typing import List, Dict
import uuid


class Receipt:
    """Receipt class for generating formal receipts from Orders"""
    
    SIMPLE = "SIMPLE"
    DETAILED = "DETAILED"
    
    def __init__(self, order, receipt_id: str = None, 
                 tax_rate: float = 0.08, tip_percent: float = 0.0):
        if not order.items:
            raise ValueError("Cannot create receipt for empty order")
        
        self.receipt_id = receipt_id or f"RCP-{uuid.uuid4().hex[:8].upper()}"
        self.order = order
        self.tax_rate = tax_rate
        self.tip_percent = tip_percent
        self.issued_at = datetime.now()
    
    def calculate_subtotal(self) -> float:
        return self.order.get_total()
    
    def calculate_tax(self) -> float:
        return self.calculate_subtotal() * self.tax_rate
    
    def calculate_tip(self) -> float:
        return self.calculate_subtotal() * self.tip_percent
    
    def calculate_total(self) -> float:
        subtotal = self.calculate_subtotal()
        tax = self.calculate_tax()
        tip = self.calculate_tip()
        return subtotal + tax + tip
    
    def generate_simple_receipt(self) -> str:
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
        
        return "\n".join(receipt_lines)
    
    def generate_detailed_receipt(self) -> str:
        receipt_lines = []
        receipt_lines.append(" " * 15 + "INVOICE / RECEIPT")
        receipt_lines.append("=" * 50)
        receipt_lines.append(f"Receipt: #{self.receipt_id:<20} Order: #{self.order.order_id}")
        receipt_lines.append(f"Customer: {self.order.customer_id}")
        receipt_lines.append(f"Date: {self.issued_at.strftime('%Y-%m-%d %I:%M %p')}")
        receipt_lines.append("=" * 50)
        
        receipt_lines.append(f"{'Item':<20} {'Qty':>5} {'Price':>8} {'Total':>10}")
        receipt_lines.append("-" * 50)
        
        for item in self.order.items:
            receipt_lines.append(
                f"{item.name[:19]:<20} "
                f"{item.quantity:>5} "
                f"${item.price:>7.2f} "
                f"${item.subtotal:>9.2f}"
            )
        
        receipt_lines.append("-" * 50)
        
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
        
        return "\n".join(receipt_lines)
    
    def get_receipt(self, receipt_type: str = SIMPLE) -> str:
        if receipt_type == self.SIMPLE:
            return self.generate_simple_receipt()
        elif receipt_type == self.DETAILED:
            return self.generate_detailed_receipt()
        else:
            raise ValueError(f"Invalid receipt type: {receipt_type}")

