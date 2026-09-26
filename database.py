import sqlite3
import re
from datetime import datetime

DB_FILE = "fasttrack.db"
ORDER_ID_PATTERN = re.compile(r"^ORD-\d{6}$")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        with open("schema.sql", "r") as f:
            conn.executescript(f.read())
    print("[OK] Database initialized (orders, tracking_history).")


def is_valid_order_id(order_id: str) -> bool:
    return bool(ORDER_ID_PATTERN.match(order_id or ""))


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_order(order_id, sender_name, receiver_name, origin, destination,
                  status="Pending"):
    if not is_valid_order_id(order_id):
        raise ValueError(f"Invalid Order ID format: '{order_id}' (expected ORD-XXXXXX)")
    if not all([sender_name, receiver_name, origin, destination]):
        raise ValueError("sender_name, receiver_name, origin, and destination are all required.")

    with get_connection() as conn:
        try:
            conn.execute(
                """INSERT INTO orders
                   (order_id, sender_name, receiver_name, origin,
                    destination, current_status, date_created)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (order_id, sender_name, receiver_name, origin, destination, status, _now())
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Order ID '{order_id}' already exists.")

    add_tracking_event(order_id, status, origin, remarks="Order created in system")
    return order_id


def add_tracking_event(order_id, status, location, remarks=None):
    if not is_valid_order_id(order_id):
        raise ValueError(f"Invalid Order ID format: '{order_id}'")
    if not get_order(order_id):
        raise ValueError(f"Cannot add tracking event: Order ID '{order_id}' does not exist.")

    with get_connection() as conn:
        conn.execute(
            """INSERT INTO tracking_history
               (order_id, status, location, timestamp, remarks)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, status, location, _now(), remarks)
        )


def update_order_status(order_id, new_status, location, remarks=None):
    if not get_order(order_id):
        raise ValueError(f"Order ID '{order_id}' does not exist.")

    with get_connection() as conn:
        conn.execute(
            "UPDATE orders SET current_status = ? WHERE order_id = ?",
            (new_status, order_id)
        )

    add_tracking_event(order_id, new_status, location, remarks)
    return True


def get_order(order_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()
    return dict(row) if row else None


def get_tracking_history(order_id):
    if not is_valid_order_id(order_id):
        raise ValueError(f"Invalid Order ID format: '{order_id}' (expected ORD-XXXXXX)")
    if not get_order(order_id):
        raise ValueError(f"No shipment found for Order ID '{order_id}'.")

    with get_connection() as conn:
        rows = conn.execute(
            """SELECT status, location, timestamp, remarks
               FROM tracking_history
               WHERE order_id = ?
               ORDER BY timestamp ASC""",
            (order_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def list_all_orders():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM orders ORDER BY date_created DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_order(order_id):
    if not get_order(order_id):
        raise ValueError(f"Order ID '{order_id}' does not exist.")
    with get_connection() as conn:
        conn.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
    return True


def seed_sample_data():
    samples = [
        ("ORD-000001", "Sanjeevani Kohli", "Lexinne Rozz Santiago", "Cebu City", "Mandaue City"),
        ("ORD-000002", "Lindy Dimaano", "Ashley Luize Galvez", "Talisay City", "Lapu-Lapu City"),
        ("ORD-000003", "Lexinne Rozz Santiago", "Sanjeevani Kohli", "Consolacion", "Cebu City"),
        ("ORD-000004", "Ashley Luize Galvez", "Lindy Dimaano", "Mandaue City", "Talisay City"),
    ]

    for order_id, sender, receiver, origin, destination in samples:
        if get_order(order_id):
            continue
        create_order(order_id, sender, receiver, origin, destination, status="Order Placed")

    histories = {
        "ORD-000001": [
            ("Picked Up", "Cebu City", "Rider collected the parcel"),
            ("In Transit", "Mandaue City Hub", "Arrived at sorting hub"),
            ("Out for Delivery", "Mandaue City", "On the way to receiver"),
        ],
        "ORD-000002": [
            ("Picked Up", "Talisay City", "Rider collected the parcel"),
        ],
        "ORD-000003": [],
        "ORD-000004": [
            ("Picked Up", "Mandaue City", "Rider collected the parcel"),
            ("In Transit", "Talisay City Hub", "Arrived at sorting hub"),
        ],
    }

    for order_id, events in histories.items():
        for status, location, remarks in events:
            add_tracking_event(order_id, status, location, remarks)
            if status in ("Picked Up", "In Transit", "Out for Delivery"):
                with get_connection() as conn:
                    conn.execute(
                        "UPDATE orders SET current_status = ? WHERE order_id = ?",
                        (status, order_id)
                    )

    print("[OK] Sample data seeded (4 orders with tracking history).")


if __name__ == "__main__":
    init_db()
    seed_sample_data()

    print("\n--- All Orders ---")
    for order in list_all_orders():
        print(f"{order['order_id']} | {order['sender_name']} -> "
              f"{order['receiver_name']} | Status: {order['current_status']}")

    print("\n--- Tracking History for ORD-000001 ---")
    for event in get_tracking_history("ORD-000001"):
        print(f"{event['timestamp']} | {event['status']:18} | "
              f"{event['location']:18} | {event['remarks']}")

    print("\n--- Error handling demo ---")
    try:
        get_tracking_history("BADID")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    try:
        get_tracking_history("ORD-999999")
    except ValueError as e:
        print(f"Caught expected error: {e}")
