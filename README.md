# SmartInvoice Pro

## API-Based QR Billing & Payment System

SmartInvoice Pro is a desktop-based billing and invoice management application developed using Python and Tkinter. It provides a complete workflow for managing products, customers, invoices, payments, QR-based payments, and sales reports.

The system integrates MySQL for data management and Razorpay Test Mode for payment processing.

---

## Project Overview

SmartInvoice Pro is designed to simplify billing and payment management for small businesses and retail environments.

The application provides:

- User authentication
- Product management
- Customer management
- Invoice creation
- Billing and cart management
- UPI QR payment generation
- Razorpay Test Mode payment integration
- Payment status tracking
- Automatic stock deduction after successful payment
- Invoice PDF generation
- Sales and payment reports
- Invoice history and details
- Automated database operations

---

## Main Features

### 1. User Authentication

- Secure login system
- Username and password authentication
- Password hashing using bcrypt
- User session management
- Role-based user information

### 2. Product Management

Users can:

- Add products
- Update products
- Delete products
- View product details
- Manage product categories
- Manage product prices
- Manage stock quantities
- Prevent duplicate product names
- Prevent deletion of products already used in invoices

### 3. Customer Management

The customer module provides:

- Add customer
- View customers
- Delete customers
- Mobile number validation
- Email validation
- Duplicate mobile number protection
- Protection against deleting customers already used in invoices

### 4. Billing

The billing module allows users to:

- Select customers
- Select products
- Add products to cart
- Set quantities
- Check available stock
- Calculate subtotals
- Calculate invoice totals
- Save invoices
- Generate payment QR codes

### 5. Invoice Management

The system provides:

- Automatic invoice number generation
- Invoice creation
- Pending and Paid invoice status
- Invoice history
- Invoice details
- Invoice item details
- Invoice PDF generation

### 6. QR Payment

The system can generate QR codes for UPI-based payment.

The QR payment workflow connects the invoice amount with the payment process.

### 7. Razorpay Payment Integration

SmartInvoice Pro integrates Razorpay Test Mode for payment processing.

The system supports:

- Payment order creation
- Razorpay checkout
- Payment cancellation handling
- Payment callback handling
- Payment verification
- Payment status updates
- Duplicate callback protection

> Razorpay is configured for testing/demo purposes. Production payment credentials should not be stored in the source code.

###