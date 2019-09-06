from mail_to_sms import MailToSMS

PHONE_NUMBER_TO_SEND = 4017495246
CARRIER = 'tmobile'

def send(message):
    MailToSMS(number=PHONE_NUMBER_TO_SEND, carrier=CARRIER, contents=message, subject="WatchTracker")
