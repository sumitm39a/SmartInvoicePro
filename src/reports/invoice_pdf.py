from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from src.database.connection import create_connection


def get_invoice_data(invoice_id: int) -> dict:
    """
    Get complete invoice information including customer and items.
    Uses the actual SmartInvoice Pro database structure.
    """

    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Get invoice + customer information.
        invoice_query = """
            SELECT
                i.invoice_id,
                i.invoice_number,
                i.invoice_date,
                i.grand_total,
                i.payment_status,
                i.remarks,
                c.customer_id,
                c.customer_name,
                c.mobile_number,
                c.email,
                c.address
            FROM invoices i
            LEFT JOIN customers c
                ON i.customer_id = c.customer_id
            WHERE i.invoice_id = %s
        """

        cursor.execute(invoice_query, (invoice_id,))
        invoice = cursor.fetchone()

        if invoice is None:
            raise ValueError(
                f"Invoice not found: invoice_id={invoice_id}"
            )

        # Get invoice items.
        items_query = """
            SELECT
                ii.invoice_item_id,
                ii.product_id,
                p.product_name,
                ii.quantity,
                ii.price_at_sale,
                ii.subtotal
            FROM invoice_items ii
            INNER JOIN products p
                ON ii.product_id = p.product_id
            WHERE ii.invoice_id = %s
            ORDER BY ii.invoice_item_id ASC
        """

        cursor.execute(items_query, (invoice_id,))
        items = cursor.fetchall()

        invoice["items"] = items

        return invoice

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def generate_invoice_pdf(invoice_id: int, output_path: str | None = None) -> str:
    """
    Generate a professional PDF invoice.

    Parameters:
        invoice_id:
            Database invoice ID.

        output_path:
            Optional path where the PDF should be saved.

    Returns:
        The full path of the generated PDF.
    """

    invoice = get_invoice_data(invoice_id)

    # Default output directory.
    if output_path is None:
        project_root = Path(__file__).resolve().parents[2]
        output_directory = project_root / "backups" / "invoices"
        output_directory.mkdir(parents=True, exist_ok=True)

        invoice_number = invoice["invoice_number"]
        output_path = output_directory / f"{invoice_number}.pdf"

    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path = output_path.resolve()

    # Create PDF document.
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Invoice {invoice['invoice_number']}",
        author="SmartInvoice Pro",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    )

    subtitle_style = ParagraphStyle(
        "InvoiceSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceAfter=3 * mm,
    )

    normal_style = ParagraphStyle(
        "InvoiceNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
    )

    right_style = ParagraphStyle(
        "InvoiceRight",
        parent=normal_style,
        alignment=TA_RIGHT,
    )

    center_style = ParagraphStyle(
        "InvoiceCenter",
        parent=normal_style,
        alignment=TA_CENTER,
    )

    story = []

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "SMARTINVOICE PRO",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "API-Based QR Billing & Payment System",
            subtitle_style,
        )
    )

    story.append(Spacer(1, 6 * mm))

    # Invoice information.
    invoice_date = invoice.get("invoice_date")

    if isinstance(invoice_date, datetime):
        formatted_date = invoice_date.strftime("%d-%m-%Y %I:%M %p")
    elif invoice_date:
        formatted_date = str(invoice_date)
    else:
        formatted_date = "-"

    invoice_info = [
        [
            Paragraph("<b>Invoice Number</b>", normal_style),
            Paragraph(str(invoice["invoice_number"]), normal_style),
            Paragraph("<b>Invoice Date</b>", normal_style),
            Paragraph(formatted_date, normal_style),
        ],
        [
            Paragraph("<b>Payment Status</b>", normal_style),
            Paragraph(str(invoice["payment_status"]), normal_style),
            Paragraph("<b>Invoice ID</b>", normal_style),
            Paragraph(str(invoice["invoice_id"]), normal_style),
        ],
    ]

    invoice_info_table = Table(
        invoice_info,
        colWidths=[
            32 * mm,
            55 * mm,
            32 * mm,
            55 * mm,
        ],
    )

    invoice_info_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("BACKGROUND", (2, 0), (2, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(invoice_info_table)
    story.append(Spacer(1, 7 * mm))

    # ---------------------------------------------------------
    # Customer information
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Bill To",
            section_style,
        )
    )

    customer_name = invoice.get("customer_name") or "-"
    mobile = invoice.get("mobile_number") or "-"
    email = invoice.get("email") or "-"
    address = invoice.get("address") or "-"

    customer_data = [
        [
            Paragraph("<b>Customer Name</b>", normal_style),
            Paragraph(str(customer_name), normal_style),
        ],
        [
            Paragraph("<b>Mobile Number</b>", normal_style),
            Paragraph(str(mobile), normal_style),
        ],
        [
            Paragraph("<b>Email</b>", normal_style),
            Paragraph(str(email), normal_style),
        ],
        [
            Paragraph("<b>Address</b>", normal_style),
            Paragraph(str(address), normal_style),
        ],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[42 * mm, 132 * mm],
    )

    customer_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(customer_table)
    story.append(Spacer(1, 7 * mm))

    # ---------------------------------------------------------
    # Purchased items
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Purchased Items",
            section_style,
        )
    )

    item_rows = [
        [
            Paragraph("<b>#</b>", center_style),
            Paragraph("<b>Product</b>", normal_style),
            Paragraph("<b>Qty</b>", center_style),
            Paragraph("<b>Price</b>", right_style),
            Paragraph("<b>Subtotal</b>", right_style),
        ]
    ]

    items = invoice.get("items", [])

    if not items:
        item_rows.append(
            [
                "",
                Paragraph("No items found.", normal_style),
                "",
                "",
                "",
            ]
        )
    else:
        for index, item in enumerate(items, start=1):
            quantity = item.get("quantity") or 0
            price = item.get("price_at_sale") or 0
            subtotal = item.get("subtotal") or 0

            item_rows.append(
                [
                    Paragraph(str(index), center_style),
                    Paragraph(
                        str(item.get("product_name") or "-"),
                        normal_style,
                    ),
                    Paragraph(str(quantity), center_style),
                    Paragraph(
                        f"₹ {float(price):,.2f}",
                        right_style,
                    ),
                    Paragraph(
                        f"₹ {float(subtotal):,.2f}",
                        right_style,
                    ),
                ]
            )

    items_table = Table(
        item_rows,
        colWidths=[
            12 * mm,
            76 * mm,
            20 * mm,
            32 * mm,
            34 * mm,
        ],
        repeatRows=1,
    )

    items_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(items_table)
    story.append(Spacer(1, 7 * mm))

    # ---------------------------------------------------------
    # Total
    # ---------------------------------------------------------

    grand_total = invoice.get("grand_total") or 0

    totals_data = [
        [
            Paragraph("<b>Grand Total</b>", right_style),
            Paragraph(
                f"<b>₹ {float(grand_total):,.2f}</b>",
                right_style,
            ),
        ]
    ]

    totals_table = Table(
        totals_data,
        colWidths=[135 * mm, 39 * mm],
    )

    totals_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(totals_table)
    story.append(Spacer(1, 7 * mm))

    # ---------------------------------------------------------
    # Remarks
    # ---------------------------------------------------------

    remarks = invoice.get("remarks")

    if remarks:
        story.append(
            Paragraph(
                "<b>Remarks</b>",
                section_style,
            )
        )

        story.append(
            Paragraph(
                str(remarks),
                normal_style,
            )
        )

        story.append(Spacer(1, 7 * mm))

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    footer_table = Table(
        [
            [
                Paragraph(
                    "Thank you for using SmartInvoice Pro.",
                    normal_style,
                ),
                Paragraph(
                    "Generated electronically",
                    right_style,
                ),
            ]
        ],
        colWidths=[105 * mm, 69 * mm],
    )

    footer_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(footer_table)

    # Build PDF.
    document.build(story)

    return str(output_path)