-- ============================================================
-- SmartInvoice Pro - Database Schema (Phase 2)
-- Database: smartinvoice_pro
-- Engine: InnoDB (required for foreign keys)
-- ============================================================

CREATE DATABASE IF NOT EXISTS smartinvoice_pro
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smartinvoice_pro;

-- ============================================================
-- 1. USERS
-- Stores application login accounts (shop owner, staff, admin)
-- Passwords are NEVER stored here — only bcrypt password_hash
-- ============================================================
CREATE TABLE users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL,   -- e.g. admin, cashier
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_users_role
        CHECK (role IN ('admin', 'cashier'))
) ENGINE=InnoDB;

CREATE INDEX idx_users_role ON users (role);


-- ============================================================
-- 2. CATEGORIES
-- Groups products (e.g. Beverages, Electronics, Stationery)
-- ============================================================
CREATE TABLE categories (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL UNIQUE,
    description     VARCHAR(255) NULL,
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- ============================================================
-- 3. PRODUCTS
-- Current catalog + live inventory
-- `price` and `stock_quantity` change over time
-- Historical sale prices are stored separately in invoice_items
-- ============================================================
CREATE TABLE products (
    product_id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id         INT NOT NULL,
    product_name        VARCHAR(150) NOT NULL,
    description         VARCHAR(255) NULL,
    price               DECIMAL(10, 2) NOT NULL,
    stock_quantity      INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 5,
    is_active           TINYINT(1) NOT NULL DEFAULT 1,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES categories (category_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_products_price
        CHECK (price >= 0),

    CONSTRAINT chk_products_stock
        CHECK (stock_quantity >= 0),

    CONSTRAINT chk_products_low_stock_threshold
        CHECK (low_stock_threshold >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_products_category_id ON products (category_id);
CREATE INDEX idx_products_name ON products (product_name);
CREATE INDEX idx_products_stock ON products (stock_quantity);


-- ============================================================
-- 4. CUSTOMERS
-- Customer master data for billing and purchase history
-- ============================================================
CREATE TABLE customers (
    customer_id     INT AUTO_INCREMENT PRIMARY KEY,
    customer_name   VARCHAR(150) NOT NULL,
    phone           VARCHAR(20) NULL,
    email           VARCHAR(100) NULL,
    address         VARCHAR(255) NULL,
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_customers_phone ON customers (phone);
CREATE INDEX idx_customers_name ON customers (customer_name);


-- ============================================================
-- 5. INVOICES
-- One row = one bill / sales transaction header
-- ============================================================
CREATE TABLE invoices (
    invoice_id      INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number  VARCHAR(30) NOT NULL UNIQUE,
    customer_id     INT NULL,               -- NULL allowed for walk-in customers
    created_by      INT NOT NULL,           -- staff user who created the bill
    subtotal        DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_amount      DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    grand_total     DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status  VARCHAR(20) NOT NULL DEFAULT 'pending',
    invoice_status  VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    notes           VARCHAR(255) NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoices_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_invoices_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_invoices_subtotal
        CHECK (subtotal >= 0),

    CONSTRAINT chk_invoices_tax_amount
        CHECK (tax_amount >= 0),

    CONSTRAINT chk_invoices_discount_amount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_invoices_grand_total
        CHECK (grand_total >= 0),

    CONSTRAINT chk_invoices_payment_status
        CHECK (payment_status IN ('pending', 'partial', 'paid', 'cancelled')),

    CONSTRAINT chk_invoices_invoice_status
        CHECK (invoice_status IN ('draft', 'confirmed', 'cancelled'))
) ENGINE=InnoDB;

CREATE INDEX idx_invoices_customer_id ON invoices (customer_id);
CREATE INDEX idx_invoices_created_by ON invoices (created_by);
CREATE INDEX idx_invoices_created_at ON invoices (created_at);
CREATE INDEX idx_invoices_payment_status ON invoices (payment_status);


-- ============================================================
-- 6. INVOICE ITEMS
-- Line items for each invoice
--
-- IMPORTANT — PRICE SNAPSHOTTING:
-- product_name and unit_price are copied at billing time.
-- Even if product price changes later, old invoices stay correct.
-- ============================================================
CREATE TABLE invoice_items (
    invoice_item_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id      INT NOT NULL,
    product_id      INT NOT NULL,
    product_name    VARCHAR(150) NOT NULL,  -- snapshot
    unit_price      DECIMAL(10, 2) NOT NULL, -- snapshot
    quantity        INT NOT NULL,
    line_total      DECIMAL(10, 2) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoice_items_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices (invoice_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_invoice_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_invoice_items_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_invoice_items_unit_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_invoice_items_line_total
        CHECK (line_total >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_invoice_items_invoice_id ON invoice_items (invoice_id);
CREATE INDEX idx_invoice_items_product_id ON invoice_items (product_id);


-- ============================================================
-- 7. PAYMENTS
-- Payment attempts/records linked to an invoice
-- Used for UPI QR billing and payment tracking
-- ============================================================
CREATE TABLE payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id      INT NOT NULL,
    amount          DECIMAL(10, 2) NOT NULL,
    payment_method  VARCHAR(20) NOT NULL DEFAULT 'upi',
    upi_reference   VARCHAR(100) NULL,
    payment_status  VARCHAR(20) NOT NULL DEFAULT 'pending',
    paid_at         TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_payments_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices (invoice_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_payments_amount
        CHECK (amount >= 0),

    CONSTRAINT chk_payments_method
        CHECK (payment_method IN ('upi', 'cash', 'card', 'other')),

    CONSTRAINT chk_payments_status
        CHECK (payment_status IN ('pending', 'completed', 'failed', 'verified'))
) ENGINE=InnoDB;

CREATE INDEX idx_payments_invoice_id ON payments (invoice_id);
CREATE INDEX idx_payments_status ON payments (payment_status);


-- ============================================================
-- 8. PAYMENT VERIFICATIONS
-- Stores results from external payment verification APIs
-- Needed for Phase 10 — audit trail of what the API returned
-- ============================================================
CREATE TABLE payment_verifications (
    verification_id     INT AUTO_INCREMENT PRIMARY KEY,
    payment_id          INT NOT NULL,
    provider            VARCHAR(50) NOT NULL,   -- e.g. razorpay, manual
    external_reference  VARCHAR(100) NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    api_response        TEXT NULL,
    verified_at         TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payment_verifications_payment
        FOREIGN KEY (payment_id)
        REFERENCES payments (payment_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_payment_verifications_status
        CHECK (verification_status IN ('pending', 'success', 'failed', 'unavailable'))
) ENGINE=InnoDB;

CREATE INDEX idx_payment_verifications_payment_id ON payment_verifications (payment_id);
CREATE INDEX idx_payment_verifications_status ON payment_verifications (verification_status);
