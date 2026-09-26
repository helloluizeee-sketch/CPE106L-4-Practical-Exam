-- ============================================================
-- FastTrack Courier System - Database Schema
-- Backend & Database Lead
-- ============================================================

-- Drop tables if re-running this script fresh
DROP TABLE IF EXISTS tracking_history;
DROP TABLE IF EXISTS orders;

-- ------------------------------------------------------------
-- Table: orders
-- Holds one row per shipment. order_id follows format ORD-000001
-- ------------------------------------------------------------
CREATE TABLE orders (
    order_id        TEXT PRIMARY KEY,          -- e.g. 'ORD-000001'
    sender_name     TEXT NOT NULL,
    receiver_name   TEXT NOT NULL,
    origin          TEXT NOT NULL,
    destination     TEXT NOT NULL,
    current_status  TEXT NOT NULL DEFAULT 'Pending',
    date_created    TEXT NOT NULL              -- ISO timestamp
);

-- ------------------------------------------------------------
-- Table: tracking_history
-- Holds every status checkpoint for every order (one-to-many
-- with orders). This is what powers the shipment timeline.
-- ------------------------------------------------------------
CREATE TABLE tracking_history (
    history_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        TEXT NOT NULL,
    status          TEXT NOT NULL,
    location        TEXT NOT NULL,
    timestamp       TEXT NOT NULL,             -- ISO timestamp
    remarks         TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON DELETE CASCADE
);

-- Index to make "look up timeline by Order ID" fast, per the
-- <1 second query requirement in the proposal.
CREATE INDEX idx_tracking_order_id ON tracking_history(order_id);
