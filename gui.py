import tkinter as tk
import database 

class CourierTrackingApp:
    """
    Main application class for the FastTrack Courier System.
    Handles the user-friendly interface and connects to the backend database.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("FastTrack Courier Tracking")
        self.root.geometry("500x450")
        self.root.configure(padx=20, pady=20)

        self.build_ui()

    def build_ui(self):
        """
        Constructs the user interface elements required for the search function.
        """
        # Header
        tk.Label(self.root, text="FastTrack Courier Portal", font=("Helvetica", 16, "bold")).pack(pady=(0, 15))

        # Search Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", pady=5)

        tk.Label(input_frame, text="Order ID:", font=("Helvetica", 12)).pack(side="left")
        self.entry_order_id = tk.Entry(input_frame, font=("Helvetica", 12))
        self.entry_order_id.pack(side="left", fill="x", expand=True, padx=10)
        
        # Search Button
        search_btn = tk.Button(self.root, text="Track Parcel", command=self.track_parcel, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
        search_btn.pack(pady=10, fill="x")

        # Dynamic Status / Error Label
        self.status_label = tk.Label(self.root, text="Format: ORD-XXXXXX (e.g., ORD-000001)", font=("Helvetica", 10), fg="gray")
        self.status_label.pack(pady=5)

        # Scrollable text area for the tracking timeline
        self.result_text = tk.Text(self.root, height=12, width=50, font=("Courier", 10), state="disabled", bg="#f4f4f4")
        self.result_text.pack(pady=10, fill="both", expand=True)

    def track_parcel(self):
        """
        Executes the search function using the imported database module.
        Retrieves the timeline and displays it in the text area.
        """
        order_id = self.entry_order_id.get().strip().upper()

        # Reset display
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")

        if not order_id:
            self.status_label.config(text="Error: Please enter an Order ID.", fg="red")
            return

        try:
            # Fulfills Use Case 3: Order ID Not Found
            order_details = database.get_order(order_id)
            if not order_details:
                self.status_label.config(text=f"Tracking Number Not Found in database.", fg="orange")
                return

            # Fulfills Use Case 1: Successful Search
            history = database.get_tracking_history(order_id)
            self.status_label.config(text="Search Successful!", fg="green")

            # Build the timeline display
            output = f"Order ID : {order_details['order_id']}\n"
            output += f"Sender   : {order_details['sender_name']}\n"
            output += f"Receiver : {order_details['receiver_name']}\n"
            output += f"Status   : {order_details['current_status']}\n"
            output += "-" * 45 + "\n"
            output += "TRACKING TIMELINE:\n"
            
            if not history:
                output += "No tracking events recorded yet.\n"
            else:
                for event in history:
                    output += f"[{event['timestamp']}]\n"
                    output += f"{event['status']} - {event['location']}\n"
                    if event['remarks']:
                        output += f"Note: {event['remarks']}\n"
                    output += "\n"

            # Render text to UI
            self.result_text.config(state="normal")
            self.result_text.insert(tk.END, output)
            self.result_text.config(state="disabled")

        except ValueError as e:
            # Fulfills Use Case 2: Data Validation Failure (Catches errors raised in database.py)
            self.status_label.config(text=str(e), fg="red")
        except Exception as e:
            self.status_label.config(text=f"System Error: Check if fasttrack.db is initialized.", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = CourierTrackingApp(root)
    root.mainloop()