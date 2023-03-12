import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(receiver: str, cc_rec: str, subj: str, html: str):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['From'] = "s.priemshiy@gmail.com"
    msg['To'] = receiver
    msg['Cc'] = cc_rec
    # msg['Bcc'] = bcc

    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    # s = smtplib.SMTP_SSL('smtp.titan.email', 465)
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)

    try:
        s.login(msg['From'], st.secrets["g_key"])
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(msg['From'], [receiver, cc_rec], msg.as_string())
        s.quit()
        return "\nMessage sent successfully!"

    except Exception as e:
        return e


ass_num = 789
ass_subject = f'New assignment {ass_num}'
ass_link = r'\\uz-fs\Uzle\Отдел ЭЛ'
ass_html = f"""
    <html>
      <head></head>
      <body>
        <h3>
          Hello, Colleague!
          <hr>
        </h3>
        <h5>
          You got this message because of new incoming assignment: {ass_num}
        </h5>
        <p>
            Please find it on your <a href="https://design-energo.streamlit.app/">site</a>
            <br>
            <br>
            or by link:<br>{ass_link}
            <hr>
            Best regards, Administration 😎
        </p>
      </body>
    </html>
"""

# print(send_mail(receiver="sergey.priemshiy@uzliti-en.com", cc_rec="p.s@email.ua", subj=ass_subject, html=ass_html))

