# ui/dialogs.py
import tkinter as tk
from tkinter import messagebox
import customtkinter
import datetime
from tkcalendar import DateEntry

class AddFulfillmentDialog(customtkinter.CTkToplevel):
    """Dialog for adding a new fulfillment entry for a BoM item."""
    def __init__(self, parent_window, bom_item_dict, controller):
        super().__init__(parent_window)
        self.transient(parent_window)
        self.grab_set()
        self.controller = controller
        self.bom_item = bom_item_dict
        self.new_fulfillment_added = False

        # Calculate remaining quantity
        current_total_fulfilled = sum(float(f.get('fulfilledQty', 0.0)) for f in self.bom_item.get('fulfillments', []) if isinstance(f, dict))
        self.item_original_qty = float(self.bom_item.get('qty', 0.0))
        self.item_remaining_qty = self.item_original_qty - current_total_fulfilled
        if self.item_remaining_qty < 0: self.item_remaining_qty = 0

        self.title(f"Add Fulfillment for: {self.bom_item.get('item', 'N/A')[:30]}")
        self.geometry("450x350")

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        # --- Widgets ---
        customtkinter.CTkLabel(main_frame, text=f"Item: {self.bom_item.get('item', 'N/A')} (SL: {self.bom_item.get('sl_no', '')})").pack(pady=2, anchor="w")
        customtkinter.CTkLabel(main_frame, text=f"Original Qty: {self.item_original_qty:.2f} | Current Remaining: {self.item_remaining_qty:.2f}").pack(pady=2, anchor="w")

        customtkinter.CTkLabel(main_frame, text="Fulfilled Quantity (this entry):").pack(pady=(10,2), anchor="w")
        self.fulfilled_qty_entry = customtkinter.CTkEntry(main_frame)
        self.fulfilled_qty_entry.pack(pady=2, fill=tk.X)
        self.fulfilled_qty_entry.focus()

        customtkinter.CTkLabel(main_frame, text="Fulfillment Date:").pack(pady=(10,2), anchor="w")
        self.date_entry_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        self.date_entry_container.pack(pady=2, fill=tk.X)
        self.fulfilled_date_entry = DateEntry(self.date_entry_container, date_pattern='dd/MM/yyyy', firstweekday='monday', width=12)
        self.fulfilled_date_entry.pack(side=tk.LEFT)
        self.fulfilled_date_entry.set_date(datetime.date.today())

        customtkinter.CTkLabel(main_frame, text="Remarks (Optional):").pack(pady=(10,2), anchor="w")
        self.remarks_entry = customtkinter.CTkEntry(main_frame)
        self.remarks_entry.pack(pady=2, fill=tk.X)

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(20,5), anchor="e")
        customtkinter.CTkButton(button_frame, text="Add Entry", command=self.submit_fulfillment).pack(side=tk.LEFT, padx=5)
        customtkinter.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="#D1D5DB", text_color="black", hover_color="#9CA3AF").pack(side=tk.LEFT, padx=5)

        # Center dialog on parent window
        self.update_idletasks()
        parent_x = parent_window.winfo_rootx()
        parent_y = parent_window.winfo_rooty()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f'+{x}+{y}')

    def submit_fulfillment(self):
        """Validates and submits the new fulfillment data."""
        try:
            qty_to_fulfill_str = self.fulfilled_qty_entry.get()
            if not qty_to_fulfill_str:
                messagebox.showerror("Input Error", "Fulfilled Quantity cannot be empty.", parent=self)
                return
            qty_to_fulfill = float(qty_to_fulfill_str)

            epsilon = 1e-9 # Tolerance for float comparison
            if qty_to_fulfill <= epsilon:
                messagebox.showerror("Input Error", "Fulfilled Quantity must be greater than zero.", parent=self)
                return
            if qty_to_fulfill > self.item_remaining_qty + epsilon:
                messagebox.showerror("Input Error", f"Fulfilled Qty ({qty_to_fulfill:.2f}) exceeds remaining Qty ({self.item_remaining_qty:.2f}).", parent=self)
                return

            fulfillment_date = self.fulfilled_date_entry.get_date().strftime("%Y-%m-%d")
            remarks = self.remarks_entry.get().strip()

            new_entry = {
                "fulfilledQty": qty_to_fulfill,
                "fulfilledDate": fulfillment_date,
                "remarks": remarks
            }

            self.bom_item.setdefault('fulfillments', []).append(new_entry)
            self.new_fulfillment_added = True
            self.destroy()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for Fulfilled Quantity.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)