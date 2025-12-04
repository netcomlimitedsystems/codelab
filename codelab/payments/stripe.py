class Session:
    def __init__(self, url):
        self.url = url

def stripe_create_session(amount, email, course_id):
    """
    Create a Stripe checkout session.
    Returns a mock session object.
    """
    url = f"/mock_stripe/checkout/{course_id}"
    print(f"[Stripe] Create session for {email}, course {course_id}, amount {amount}")
    return Session(url=url)

def stripe_verify_payment(session_id):
    """
    Verify Stripe payment after checkout.
    """
    print(f"[Stripe] Verify session {session_id}")
    return True
