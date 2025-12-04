def mpesa_pay(phone_number, amount, course_id, user_id):
    """
    Initiates an M-Pesa STK push payment.
    For now, this is a placeholder that always succeeds.
    """
    # In real integration:
    # - Call Safaricom Daraja API
    # - Send amount, phone_number, account ref (course_id)
    # - Return success/failure + transaction_id
    print(f"[M-Pesa] Initiate payment for user {user_id}, course {course_id}, amount {amount}, phone {phone_number}")
    return {"success": True, "message": "STK push initiated"}

def verify_mpesa_payment(transaction_id, user_id, course_id):
    """
    Verify M-Pesa payment.
    """
    print(f"[M-Pesa] Verifying transaction {transaction_id} for user {user_id}, course {course_id}")
    # Placeholder always returns True
    return True
