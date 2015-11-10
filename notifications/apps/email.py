from ._base_alert import BaseAlert
from sensors.models import SensorData

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

class Email(BaseAlert):
    def alert(self):
        self.subject = "%s Temperature Alert - %s 'F" % (self.sensor.name, self.sensor_data.value_f())
        self.message = "Please check %s at %s, temperature monitoring reports %s 'F." % (self.sensor.name, self.sensor.zone.name, self.sensor_data.value_f())

    def down(self):
        self.subject = "%s Temperature Monitoring Unavailable" % (self.sensor.name)
        self.message = "Please check %s at %s, temperature monitoring is currently down. Internet or device issue." % (self.sensor.name, self.sensor.zone.name)

    def recovered(self):
        self.subject = "%s Temperature is OK - %s 'F" % (self.sensor.name, self.sensor_data.value_f())
        self.message = "Temperature of %s at %s appears to have recovered, now reporting %s 'F." % (self.sensor.name, self.sensor.zone.name, self.sensor_data.value_f())

    def setup(self):
        self.recipients = []
        users = self.sensor.get_alert_users()
        for user in users:
            if user.email:
                self.recipients.append(user.email)

    def send(self):

        message_text = get_template("email/email_template.txt")
        message_html = get_template("email/email_template.html")

        sensor_data_history = SensorData.objects.filter(sensor=self.sensor).order_by('-datetime')[:10]
        d = Context({
                    'message': self.message, 
                    'sensor': self.sensor, 
                    'sensor_data': sensor_data_history,
                })

        text_content = message_text.render(d)
        html_content = message_html.render(d)

        msg = EmailMultiAlternatives(self.subject, text_content, self.settings["FROM_ADDRESS"], self.recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
