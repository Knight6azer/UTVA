import json
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.font import Font
import os

class VegetableMarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍅 Fresh Vegetable Market - Vendor App")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f8f0')
        
        self.vegetables_db = {
            "🥬 Leafy Greens": {"Spinach": 10, "Lettuce": 12, "Cabbage": 15, "Kale": 18, "Arugula": 20},
            "🥕 Root Vegetables": {"Potato": 8, "Carrot": 10, "Beetroot": 9, "Onion": 6, "Garlic": 15},
            "🍅 Fruit Vegetables": {"Tomato": 7, "Cucumber": 6, "Capsicum": 12, "Eggplant": 11, "Zucchini": 9}
        }
        
        self.all_vegetables = {veg: price for cat in self.vegetables_db.values() for veg, price in cat.items()}
        self.user_stack = []
        self.order_queue = deque()
        self.cart = {}
        
        self.setup_styles()
        
        self.main_frame = ttk.Frame(root, style='Main.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_header()
        
        self.content_frame = ttk.Frame(self.main_frame, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        self.create_left_panel()
        self.create_right_panel()
        
        self.update_cart_display()
        
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Main.TFrame', background='#f0f8f0')
        style.configure('Content.TFrame', background='#ffffff')
        style.configure('Header.TLabel', 
                       background='#2e7d32', 
                       foreground='white', 
                       font=('Arial', 16, 'bold'),
                       padding=15)
        style.configure('Title.TLabel', 
                       background='#ffffff', 
                       foreground='#2e7d32', 
                       font=('Arial', 12, 'bold'),
                       padding=5)
        style.configure('Info.TLabel', 
                       background='#ffffff', 
                       foreground='#666666',
                       font=('Arial', 10),
                       padding=3)
        style.configure('Action.TButton', 
                       background='#4caf50',
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        style.configure('Danger.TButton', 
                       background='#f44336',
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        style.configure('Success.TButton', 
                       background='#2196f3',
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
    def create_header(self):
        """Create the application header"""
        header_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_label = ttk.Label(header_frame, 
                                text="🍅 Fresh Vegetable Market - Vendor App", 
                                style='Header.TLabel')
        header_label.pack(fill='x')
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Professional Inventory Management System", 
                                  style='Info.TLabel')
        subtitle_label.pack()
        
    def create_left_panel(self):
        """Create the left panel for product selection and cart management"""
        left_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        selection_frame = ttk.LabelFrame(left_frame, text="🛒 Product Selection", padding=15)
        selection_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(selection_frame, text="Category:", style='Title.TLabel').pack(anchor='w')
        self.category_var = tk.StringVar()
        self.category_var.set(list(self.vegetables_db.keys())[0])
        self.category_var.trace('w', self.update_vegetable_options)
        
        category_combo = ttk.Combobox(selection_frame, 
                                     textvariable=self.category_var,
                                     values=list(self.vegetables_db.keys()),
                                     state='readonly',
                                     font=('Arial', 10))
        category_combo.pack(fill='x', pady=(5, 10))
        
        ttk.Label(selection_frame, text="Vegetable:", style='Title.TLabel').pack(anchor='w')
        self.veg_var = tk.StringVar()
        self.veg_combo = ttk.Combobox(selection_frame, 
                                     textvariable=self.veg_var,
                                     state='readonly',
                                     font=('Arial', 10))
        self.veg_combo.pack(fill='x', pady=(5, 10))
        
        self.price_label = ttk.Label(selection_frame, text="Price: ₹0", style='Info.TLabel')
        self.price_label.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(selection_frame, text="Quantity:", style='Title.TLabel').pack(anchor='w')
        self.qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(selection_frame, 
                             textvariable=self.qty_var,
                             font=('Arial', 10),
                             justify='center')
        qty_entry.pack(fill='x', pady=(5, 15))
        
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, 
                  text="➕ Add to Cart", 
                  command=self.add_to_cart,
                  style='Action.TButton').pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(button_frame, 
                  text="➖ Remove from Cart", 
                  command=self.remove_from_cart,
                  style='Danger.TButton').pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        self.update_vegetable_options()
        
    def create_right_panel(self):
        """Create the right panel for cart display and order management"""
        right_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        cart_frame = ttk.LabelFrame(right_frame, text="🛍️ Shopping Cart", padding=15)
        cart_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.cart_text = scrolledtext.ScrolledText(cart_frame, 
                                                  height=15, 
                                                  width=40,
                                                  font=('Consolas', 9),
                                                  bg='#fafafa',
                                                  fg='#333333')
        self.cart_text.pack(fill='both', expand=True, pady=(0, 10))
        
        self.cart_summary = ttk.Label(cart_frame, text="Total: ₹0 | Items: 0", style='Title.TLabel')
        self.cart_summary.pack(anchor='w')
        
        order_frame = ttk.LabelFrame(right_frame, text="📋 Order Management", padding=15)
        order_frame.pack(fill='x')
        
        ttk.Label(order_frame, text="Receipt Sort Order:", style='Title.TLabel').pack(anchor='w')
        self.sort_var = tk.StringVar(value="Alphabetical")
        sort_combo = ttk.Combobox(order_frame, 
                                 textvariable=self.sort_var,
                                 values=["Alphabetical", "By Price (Low to High)", "By Price (High to Low)"],
                                 state='readonly',
                                 font=('Arial', 10))
        sort_combo.pack(fill='x', pady=(5, 15))
        
        ttk.Button(order_frame, 
                  text="🧹 Clear Cart", 
                  command=self.clear_cart,
                  style='Danger.TButton').pack(fill='x', pady=(0, 5))
        
        ttk.Button(order_frame, 
                  text="📄 Generate Receipt", 
                  command=self.generate_receipt,
                  style='Success.TButton').pack(fill='x', pady=(0, 5))
        
        ttk.Button(order_frame, 
                  text="💾 Save Order to JSON", 
                  command=self.save_order,
                  style='Action.TButton').pack(fill='x')
        
    def update_vegetable_options(self, *args):
        """Update vegetable options based on selected category"""
        category = self.category_var.get()
        vegetables = list(self.vegetables_db[category].keys())
        self.veg_combo['values'] = vegetables
        if vegetables:
            self.veg_var.set(vegetables[0])
            self.update_price_display()
            
    def update_price_display(self, *args):
        """Update price display for selected vegetable"""
        veg = self.veg_var.get()
        if veg in self.all_vegetables:
            price = self.all_vegetables[veg]
            self.price_label.config(text=f"Price: ₹{price}")
            
    def add_to_cart(self):
        """Add selected vegetable to cart"""
        veg = self.veg_var.get()
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
                
            for _ in range(qty):
                self.user_stack.append(veg)
                
            self.update_cart_display()
            
            messagebox.showinfo("✅ Added", f"{qty} x {veg.title()} added to cart successfully!")
            
        except ValueError:
            messagebox.showerror("❌ Invalid Input", "Please enter a valid positive integer for quantity.")
            
    def remove_from_cart(self):
        """Remove selected vegetable from cart"""
        veg = self.veg_var.get()
        try:
            qty = int(self.qty_var.get())
            removed = 0
            
            for _ in range(qty):
                if veg in self.user_stack:
                    self.user_stack.remove(veg)
                    removed += 1
                    
            if removed:
                self.update_cart_display()
                messagebox.showinfo("✅ Removed", f"Removed {removed} x {veg.title()} from cart.")
            else:
                messagebox.showinfo("ℹ️ Not Found", f"No {veg.title()} found in cart.")
                
        except ValueError:
            messagebox.showerror("❌ Invalid Input", "Please enter a valid number to remove.")
            
    def update_cart_display(self):
        """Update the cart display with current items"""
        self.cart_text.delete(1.0, tk.END)
        
        if not self.user_stack:
            self.cart_text.insert(tk.END, "Your cart is empty.\nAdd some vegetables!")
            self.cart_summary.config(text="Total: ₹0 | Items: 0")
            return
            
        cart_count = {}
        for item in self.user_stack:
            cart_count[item] = cart_count.get(item, 0) + 1
            
        total = 0
        items_count = len(self.user_stack)
        
        self.cart_text.insert(tk.END, f"{'Item':<15} {'Qty':<5} {'Price':<8} {'Total':<10}\n")
        self.cart_text.insert(tk.END, "-" * 40 + "\n")
        
        for veg, qty in cart_count.items():
            price = self.all_vegetables[veg]
            line_total = price * qty
            total += line_total
            
            self.cart_text.insert(tk.END, f"{veg.title():<15} {qty:<5} ₹{price:<7} ₹{line_total:<9}\n")
            
        self.cart_text.insert(tk.END, "-" * 40 + "\n")
        self.cart_text.insert(tk.END, f"{'TOTAL':<15} {items_count:<5} {'':<8} ₹{total:<9}\n")
        
        self.cart_summary.config(text=f"Total: ₹{total} | Items: {items_count}")
        
    def clear_cart(self):
        """Clear all items from cart"""
        if self.user_stack:
            self.user_stack.clear()
            self.update_cart_display()
            messagebox.showinfo("🧹 Cleared", "Cart has been cleared successfully!")
        else:
            messagebox.showinfo("ℹ️ Empty", "Cart is already empty.")
            
    def generate_receipt(self):
        """Generate and display receipt"""
        if not self.user_stack:
            messagebox.showwarning("⚠️ Empty Cart", "Cannot generate receipt for empty cart!")
            return
            
        self.cart.clear()
        while self.user_stack:
            item = self.user_stack.pop()
            self.order_queue.append(item)
            
        for item in self.order_queue:
            if item in self.cart:
                self.cart[item] += 1
            else:
                self.cart[item] = 1
                
        sort_option = self.sort_var.get()
        if sort_option == "Alphabetical":
            sorted_items = sorted(self.cart.items())
        elif sort_option == "By Price (Low to High)":
            sorted_items = sorted(self.cart.items(), key=lambda x: self.all_vegetables[x[0]])
        else: 
            sorted_items = sorted(self.cart.items(), key=lambda x: self.all_vegetables[x[0]], reverse=True)
            
        total = 0
        receipt = "=" * 50 + "\n"
        receipt += "           FRESH VEGETABLE MARKET\n"
        receipt += "=" * 50 + "\n"
        receipt += f"{'Item':<20} {'Qty':<8} {'Price':<10} {'Total':<12}\n"
        receipt += "-" * 50 + "\n"
        
        for veg, qty in sorted_items:
            price = self.all_vegetables[veg]
            line_total = price * qty
            total += line_total
            receipt += f"{veg.title():<20} {qty:<8} ₹{price:<9} ₹{line_total:<11}\n"
            
        receipt += "-" * 50 + "\n"
        receipt += f"{'TOTAL':<20} {sum(self.cart.values()):<8} {'':<10} ₹{total:<11}\n"
        receipt += "=" * 50 + "\n"
        receipt += "Thank you for your purchase!\n"
        receipt += "=" * 50 + "\n"
        
        with open("receipt.txt", "w", encoding='utf-8') as txt_file:
            txt_file.write(receipt)
            
        self.show_receipt_window(receipt)
        
        self.user_stack.clear()
        self.update_cart_display()
        
    def show_receipt_window(self, receipt):
        """Show receipt in a new window"""
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("📄 Receipt")
        receipt_window.geometry("600x500")
        receipt_window.configure(bg='#ffffff')
        
        receipt_text = scrolledtext.ScrolledText(receipt_window, 
                                                font=('Courier', 10),
                                                bg='#ffffff',
                                                fg='#000000',
                                                wrap='word')
        receipt_text.pack(fill='both', expand=True, padx=20, pady=20)
        receipt_text.insert(tk.END, receipt)
        receipt_text.config(state='disabled')
        
        ttk.Button(receipt_window, 
                  text="Close", 
                  command=receipt_window.destroy,
                  style='Action.TButton').pack(pady=(0, 20))
        
    def save_order(self):
        """Save current cart to JSON file"""
        if not self.user_stack:
            messagebox.showwarning("⚠️ Empty Cart", "Cannot save empty cart!")
            return
            
        cart_count = {}
        for item in self.user_stack:
            cart_count[item] = cart_count.get(item, 0) + 1
            
        with open("order.json", "w", encoding='utf-8') as f:
            json.dump(cart_count, f, indent=4, ensure_ascii=False)
            
        messagebox.showinfo("💾 Saved", "Order has been saved to 'order.json' successfully!")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = VegetableMarketApp(root)
    
    app.veg_combo.bind('<<ComboboxSelected>>', app.update_price_display)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 