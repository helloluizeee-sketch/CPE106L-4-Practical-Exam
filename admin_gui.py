import tkinter as tk
from tkinter import ttk, messagebox
import database

class AdminDashboard:
    """
    Dispatcher/Admin interface for the FastTrack Courier System.
    Handles data entry for new parcels and status checkpoint updates.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("FastTrack Admin Dashboard")
        self.root.geometry("500x550")
        self.root.configure(padx=15, pady=15)

        # Create tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_register = ttk.Frame(self.notebook)
        self.tab_update = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_register, text="Register New Parcel")
        self.notebook.add(self.tab_update, text="Update Status")

        self.build_register_tab()
        self.build_update_tab()

    def build_register_tab(self):
        """Builds the UI for registering a new shipment."""
        tk.Label(self.tab_register, text="Register Parcel", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Input fields
        self.reg_order_id = self.create_input_row(self.tab_register, "Order ID (ORD-XXXXXX):")
        self.reg_sender = self.create_input_row(self.tab_register, "Sender Name:")
        self.reg_receiver = self.create_input_row(self.tab_register, "Receiver Name:")
        self.reg_origin = self.create_input_row(self.tab_register, "Origin:")
        self.reg_dest = self.create_input_row(self.tab_register, "Destination:")

        # Register Button
        btn = tk.Button(self.tab_register, text="Register Parcel", command=self.register_parcel, bg="#2196F3", fg="white", font=("Helvetica", 11, "bold"))
        btn.pack(pady=20, fill="x", padx=20)

    def build_update_tab(self):
        """Builds the UI for adding tracking events."""
        tk.Label(self.tab_update, text="Log Tracking Event", font=("Helvetica", 14, "bold")).pack(pady=10)

        self.upd_order_id = self.create_input_row(self.tab_update, "Order ID:")
        
        # Status Dropdown
        frame = tk.Frame(self.tab_update)
        frame.pack(fill="x", pady=5, padx=20)
        tk.Label(frame, text="New Status:", width=18, anchor="w").pack(side="left")
        self.upd_status = ttk.Combobox(frame, values=["Picked Up", "In Transit", "Out for Delivery", "Delivered"], state="readonly")
        self.upd_status.set("Picked Up")
        self.upd_status.pack(side="left", fill="x", expand=True)

        self.upd_location = self.create_input_row(self.tab_update, "Current Location:")
        self.upd_remarks = self.create_input_row(self.tab_update, "Remarks (Optional):")

        # Update Button
        btn = tk.Button(self.tab_update, text="Update Checkpoint", command=self.update_status, bg="#FF9800", fg="white", font=("Helvetica", 11, "bold"))
        btn.pack(pady=20, fill="x", padx=20)

    def create_input_row(self, parent, label_text):
        """Helper function to create consistent input rows."""
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=5, padx=20)
        tk.Label(frame, text=label_text, width=18, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def register_parcel(self):
        """Executes the create_order backend function."""
        order_id = self.reg_order_id.get().strip().upper()
        sender = self.reg_sender.get().strip()
        receiver = self.reg_receiver.get().strip()
        origin = self.reg_origin.get().strip()
        dest = self.reg_dest.get().strip()

        try:
            database.create_order(order_id, sender, receiver, origin, dest)
            messagebox.showinfo("Success", f"Parcel {order_id} registered successfully!")
            # Clear fields
            for field in (self.reg_order_id, self.reg_sender, self.reg_receiver, self.reg_origin, self.reg_dest):
                field.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Database Error", "Ensure fasttrack.db is initialized.")

    def update_status(self):
        """Executes the update_order_status backend function."""
        order_id = self.upd_order_id.get().strip().upper()
        status = self.upd_status.get()
        location = self.upd_location.get().strip()
        remarks = self.upd_remarks.get().strip() or None

        if not location:
            messagebox.showerror("Validation Error", "Current Location is required.")
            return

        try:
            database.update_order_status(order_id, status, location, remarks)
            messagebox.showinfo("Success", f"Tracking timeline updated for {order_id}!")
            self.upd_order_id.delete(0, tk.END)
            self.upd_location.delete(0, tk.END)
            self.upd_remarks.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()