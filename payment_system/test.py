import os
from django.utils import timezone

from rest_framework.views import APIView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from data_converter.settings_local import SENDGRID_API_KEY
from payment_system.models import Invoice, DailyReport


class mailed(APIView):
    def __init__(self):
        should_complete = ''
        should_complete_counter = 0
        was_complete = ''
        was_complete_counter = 0
        was_overdue = ''
        was_overdue_counter = 0
        message_text = ''
        for one in Invoice.objects.all():
            email = one.project_subscription.project.owner.email
            line = str(one.project_subscription) + ' | ' + one.project_name + ' | ' + str(
                one.id) + ' | ' + email + '<br>'
            if one.paid_at is None:
                if one.start_date == timezone.localdate():
                    should_complete += line
                    should_complete_counter += 1
                elif one.start_date == (timezone.localdate() - timezone.timedelta(days=1)):
                    was_overdue += line
                    was_overdue_counter += 1
            elif one.start_date == timezone.localdate():
                was_complete += line
                was_complete_counter += 1

        DailyReport.objects.create(
            created_at=timezone.localdate(),
            should_complete_count=should_complete_counter,
            was_complete_count=was_complete_counter,
            was_overdue_count=was_overdue_counter,
        )

        message_text += 'Should be completed ' + str(should_complete_counter) + '<br>' + should_complete + \
                        '<br>' + 'Was overdue: ' + str(was_overdue_counter) + '<br>' + was_overdue + \
                        '<br>' + 'Was completed:' + str(was_complete_counter) + '<br>' + was_complete

        message = Mail(
            from_email='viktor6ivanov@gmail.com',
            to_emails='viktor6ivanov@gmail.com',
            subject='Daily payments report',
            html_content=message_text
        )
        key = SENDGRID_API_KEY
        try:
            sg = SendGridAPIClient(key)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
