import time

from conduit.app import celery


@celery.task()
def send_email(username, code, user_email):
    import os
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from conduit.template.html_template import (
        htmlFile, textFile
    )

    EMAIL_ADD_GMAIL = os.environ.get('EMAIL_USER_GMAIL')
    EMAIL_PASS_GMAIL = os.environ.get('EMAIL_PASSWORD_GMAIL')
    EMAIL_ADD_YAHOO = os.environ.get('EMAIL_USER_YAHOO')
    EMAIL_PASS_YAHOO = os.environ.get('EMAIL_PASSWORD_YAHOO')

    msg = MIMEMultipart('alternative')

    msg['Subject'] = f'Verification code for Documenter'
    msg['From'] = EMAIL_ADD_GMAIL
    msg['To'] = EMAIL_ADD_GMAIL
    # msg['To'] = user_email

    link = f'http://127.0.0.1:5000/link-verify/?username={username}&code={code}'
    new_text_file = textFile.replace('username-here', username)
    new_text_file = new_text_file.replace('code-here', code)
    new_text_file = new_text_file.replace('link-here', link)

    new_html_file = htmlFile.replace('username-here', username)
    new_html_file = new_html_file.replace('code-here', code)
    new_html_file = new_html_file.replace('link-here', link)

    part_text = MIMEText(new_text_file, 'plain')
    part_html = MIMEText(new_html_file, 'html')

    msg.attach(part_text)
    msg.attach(part_html)

    success = smtp_send_off('smtp.gmail.com', EMAIL_ADD_GMAIL, EMAIL_PASS_GMAIL, msg)

    if not success:
        retry = smtp_send_off('smtp.mail.yahoo.com', EMAIL_ADD_YAHOO, EMAIL_PASS_YAHOO, msg)

        return retry
    else:
        return success
    return False


def smtp_send_off(smtp_server, email_address, email_password, msg):
    import smtplib

    with smtplib.SMTP_SSL(smtp_server, 465) as smtp:
        smtp.login(email_address, email_password)
        try:
            smtp.send_message(msg)
            print("email sent!")
            return True
        except smtplib.SMTPResponseException as err:
            print("error sending code!")
            print(err)
            return False


@celery.task()
def password_attempt_timeout():
    time.sleep(600)

    return True