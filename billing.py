import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import tempfile
from datetime import datetime

APP_NAME = "Diamond's Student Point"


class BillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("850x650")
        self.root.resizable(False, False)

        self.items = []

        self.rate_var = tk.StringVar()
        self.qty_var = tk.StringVar(value="1")
        self.discount_var = tk.StringVar(value="0")
        self.payment_var = tk.StringVar(value="CASH")
        self.received_var = tk.StringVar(value="0")

        self.subtotal_var = tk.StringVar(value="₹0.00")
        self.total_var = tk.StringVar(value="₹0.00")
        self.change_var = tk.StringVar(value="₹0.00")

        self.create_ui()

    def create_ui(self):

        title = tk.Label(
            self.root,
            text="DIAMOND'S STUDENT POINT",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=(20, 3))

        subtitle = tk.Label(
            self.root,
            text="Stationery & Student Needs",
            font=("Arial", 11)
        )
        subtitle.pack()

        # ---------------- ADD ITEM ----------------

        item_frame = tk.LabelFrame(
            self.root,
            text="Add Item",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        item_frame.pack(fill="x", padx=25, pady=20)

        tk.Label(item_frame, text="Rate").grid(
            row=0, column=0, padx=10
        )

        rate_entry = tk.Entry(
            item_frame,
            textvariable=self.rate_var,
            width=15,
            font=("Arial", 12)
        )
        rate_entry.grid(row=0, column=1, padx=10)

        tk.Label(item_frame, text="Qty").grid(
            row=0, column=2, padx=10
        )

        qty_entry = tk.Entry(
            item_frame,
            textvariable=self.qty_var,
            width=10,
            font=("Arial", 12)
        )
        qty_entry.grid(row=0, column=3, padx=10)

        tk.Button(
            item_frame,
            text="ADD",
            width=12,
            font=("Arial", 11, "bold"),
            command=self.add_item
        ).grid(row=0, column=4, padx=15)

        # ---------------- ITEM TABLE ----------------

        self.tree = ttk.Treeview(
            self.root,
            columns=("no", "rate", "qty", "amount"),
            show="headings",
            height=12
        )

        self.tree.heading("no", text="#")
        self.tree.heading("rate", text="Rate")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("amount", text="Amount")

        self.tree.column("no", width=60, anchor="center")
        self.tree.column("rate", width=180, anchor="center")
        self.tree.column("qty", width=150, anchor="center")
        self.tree.column("amount", width=200, anchor="center")

        self.tree.pack(fill="x", padx=25)

        tk.Button(
            self.root,
            text="DELETE SELECTED",
            command=self.delete_item
        ).pack(pady=8)

        # ---------------- PAYMENT ----------------

        payment_frame = tk.LabelFrame(
            self.root,
            text="Payment",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=12
        )
        payment_frame.pack(fill="x", padx=25, pady=10)

        tk.Label(payment_frame, text="Subtotal").grid(
            row=0, column=0, padx=10
        )

        tk.Label(
            payment_frame,
            textvariable=self.subtotal_var,
            font=("Arial", 11, "bold")
        ).grid(row=0, column=1, padx=10)

        tk.Label(payment_frame, text="Discount").grid(
            row=0, column=2, padx=10
        )

        discount_entry = tk.Entry(
            payment_frame,
            textvariable=self.discount_var,
            width=10
        )
        discount_entry.grid(row=0, column=3, padx=10)

        discount_entry.bind(
            "<KeyRelease>",
            lambda e: self.calculate()
        )

        tk.Label(payment_frame, text="Payment").grid(
            row=0, column=4, padx=10
        )

        payment_box = ttk.Combobox(
            payment_frame,
            textvariable=self.payment_var,
            values=["CASH", "UPI"],
            state="readonly",
            width=10
        )
        payment_box.grid(row=0, column=5, padx=10)

        tk.Label(payment_frame, text="Received").grid(
            row=1, column=0, padx=10, pady=10
        )

        received_entry = tk.Entry(
            payment_frame,
            textvariable=self.received_var,
            width=12
        )
        received_entry.grid(row=1, column=1, padx=10)

        received_entry.bind(
            "<KeyRelease>",
            lambda e: self.calculate()
        )

        tk.Label(payment_frame, text="Change").grid(
            row=1, column=2, padx=10
        )

        tk.Label(
            payment_frame,
            textvariable=self.change_var,
            font=("Arial", 11, "bold")
        ).grid(row=1, column=3, padx=10)

        tk.Label(payment_frame, text="TOTAL").grid(
            row=1, column=4, padx=10
        )

        tk.Label(
            payment_frame,
            textvariable=self.total_var,
            font=("Arial", 16, "bold")
        ).grid(row=1, column=5, padx=10)

        # ---------------- BUTTONS ----------------

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="CLEAR BILL",
            width=15,
            command=self.clear_bill
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="SAVE & PRINT",
            width=20,
            font=("Arial", 11, "bold"),
            command=self.save_and_print
        ).pack(side="left", padx=10)

    # ---------------- FUNCTIONS ----------------

    def add_item(self):

        try:
            rate = float(self.rate_var.get())
            qty = float(self.qty_var.get())

            if rate <= 0 or qty <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid",
                "Enter a valid rate and quantity."
            )
            return

        amount = rate * qty

        self.items.append(
            (rate, qty, amount)
        )

        self.refresh_table()

        self.rate_var.set("")
        self.qty_var.set("1")

        self.calculate()

    def refresh_table(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, item in enumerate(self.items, 1):

            rate, qty, amount = item

            self.tree.insert(
                "",
                "end",
                values=(
                    i,
                    f"{rate:.2f}",
                    f"{qty:g}",
                    f"{amount:.2f}"
                )
            )

    def delete_item(self):

        selected = self.tree.selection()

        if not selected:
            return

        indexes = sorted(
            [self.tree.index(x) for x in selected],
            reverse=True
        )

        for index in indexes:
            del self.items[index]

        self.refresh_table()
        self.calculate()

    def calculate(self):

        subtotal = sum(
            item[2] for item in self.items
        )

        try:
            discount = float(
                self.discount_var.get() or 0
            )
        except ValueError:
            discount = 0

        total = max(
            0,
            subtotal - discount
        )

        try:
            received = float(
                self.received_var.get() or 0
            )
        except ValueError:
            received = 0

        change = max(
            0,
            received - total
        )

        self.subtotal_var.set(
            f"₹{subtotal:.2f}"
        )

        self.total_var.set(
            f"₹{total:.2f}"
        )

        self.change_var.set(
            f"₹{change:.2f}"
        )

    def clear_bill(self):

        self.items.clear()

        self.refresh_table()

        self.rate_var.set("")
        self.qty_var.set("1")
        self.discount_var.set("0")
        self.received_var.set("0")

        self.calculate()

    def save_and_print(self):

        if not self.items:
            messagebox.showwarning(
                "Empty Bill",
                "Please add at least one item."
            )
            return

        self.calculate()

        messagebox.showinfo(
            "Ready",
            "Billing system is working.\n\n"
            "Printing will be added after we confirm the app opens correctly."
        )


if __name__ == "__main__":

    root = tk.Tk()

    app = BillingApp(root)

    root.mainloop()
