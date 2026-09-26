import tkinter as tk
import sqlite3
import re

class CourierTrackingApp:
    """
    Main application class for the FastTrack Courier System.
    Handles the user-friendly interface, database connection, and search functionality.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("FastTrack Courier Tracking")
        self.root.geometry("400x300")
        self.root.configure(padx=20, pady=20)

        # Initialize local database for the submission requirement
        self.setup_database()

        # Construct the UI components
        self.build_ui()

    def setup_database(self):
        """
        Initializes a local SQLite database and populates it with sample data
        to execute the minimum testing use cases.
        """
        self.conn = sqlite3.connect("courier_tracking.db")
        self.cursor = self.conn.cursor()
        
        # Create the tracking table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parcels (
                order_id TEXT PRIMARY KEY,
                status TEXT,
                location TEXT
            )
        ''')
        
        # Insert sample data for Use Case 1 (Successful Search)
        self.cursor.execute("INSERT OR IGNORE INTO parcels VALUES ('ORD1001', 'In Transit', 'Manila Sorting Hub')")
        self.cursor.execute("INSERT OR IGNORE INTO parcels VALUES ('ORD1002', 'Out for Delivery', 'Las Piñas Branch')")
        self.conn.commit()

    def build_ui(self):
        """
        Constructs the user interface elements required for the search function.
        """
        # Header 
        title_label = tk.Label(self.root, text="Courier Tracking Portal", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Search Bar Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", pady=5)

        tk.Label(input_frame, text="Order ID:", font=("Helvetica", 12)).pack(side="left")
        self.entry_order_id = tk.Entry(input_frame, font=("Helvetica", 12))
        self.entry_order_id.pack(side="left", fill="x", expand=True, padx=10)

        # Search Button
        search_btn = tk.Button(self.root, text="Track Parcel", command=self.track_parcel, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
        search_btn.pack(pady=15, fill="x")

        # Dynamic Status Display Area
        self.result_label = tk.Label(self.root, text="Enter an Order ID to begin.", font=("Helvetica", 11), fg="gray", justify="center")
        self.result_label.pack(pady=10)

    def validate_input(self, order_id):
        """
        Executes data validation to ensure user input meets system requirements.
        Rejects empty strings or entries containing special characters.
        """
        if not order_id:
            return False, "Error: Order ID cannot be empty."
        
        # Enforce alphanumeric format using regular expressions
        if not re.match(r"^[A-Za-z0-9]+$", order_id):
            return False, "Error: Invalid format. Use alphanumeric characters only."
        
        return True, "Valid"

    def track_parcel(self):
        """
        Executes the search function based on the validated Order ID.
        Updates the UI with the parcel status or an appropriate error prompt.
        """
        order_id = self.entry_order_id.get().strip()

        # Fulfills Use Case 2: Data Validation Failure
        is_valid, validation_msg = self.validate_input(order_id)
        if not is_valid:
            self.result_label.config(text=validation_msg, fg="red")
            return

        # Fulfills Use Case 1 & 3: Executing Database Search
        self.cursor.execute("SELECT status, location FROM parcels WHERE order_id = ?", (order_id.upper(),))
        result = self.cursor.fetchone()

        if result:
            # Fulfills Use Case 1: Successful Search
            status, location = result
            self.result_label.config(text=f"Status: {status}\nCurrent Location: {location}", fg="green")
        else:
            # Fulfills Use Case 3: Order ID Not Found
            self.result_label.config(text="Tracking Number Not Found in database.", fg="orange")

if __name__ == "__main__":
    root = tk.Tk()
    app = CourierTrackingApp(root)
    root.mainloop()