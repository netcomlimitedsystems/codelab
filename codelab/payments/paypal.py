def paypal_create_order(amount, email, course_id):
    """
    Create a PayPal order.
    Returns a mock approval URL.
    """
    approval_url = f"/mock_paypal/checkout/{course_id}"
    print(f"[PayPal] Create order for {email}, course {course_id}, amount {amount}")
    return {"approval_url": approval_url}

def paypal_capture_order(order_id):
    """
    Capture PayPal payment after user approves it.
    """
    print(f"[PayPal] Capture order {order_id}")
    # Placeholder returns True
    return True
