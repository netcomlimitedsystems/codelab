from django.core.mail import EmailMessage

def send_certificate_email(user, certificate):
    subject = f"Your Certificate for {certificate.course.title}"
    body = (
        f"Congratulations {user.get_full_name() or user.username}!\n\n"
        f"You have successfully completed the course: {certificate.course.title}\n"
        "Please find your certificate attached.\n\n"
        "Regards,\nCodelab Team"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[user.email]
    )

    # Attach the certificate PDF if it exists
    if certificate.file:
        certificate.file.open('rb')  # Open the file
        email.attach(certificate.file.name, certificate.file.read(), 'application/pdf')
        certificate.file.close()  # Close the file after reading

    email.send(fail_silently=False)
