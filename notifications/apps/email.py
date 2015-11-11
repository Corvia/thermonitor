from ._base_alert import BaseAlert
from sensors.models import SensorData
from notifications.models import SensorAlert

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

class Email(BaseAlert):
    # Sensor is failing and outside of temperature threshold checks.
    def alert(self):
        self.subject = "%s Temperature Alert - %s 'F" % (self.sensor.name, self.sensor_data.value_f())
        self.message = "Please check %s at %s, temperature monitoring reports %s 'F." % (self.sensor.name, self.sensor.zone.name, self.sensor_data.value_f())

    # Sensor is late to report in or unavailable.
    def down(self):
        self.subject = "%s Temperature Monitoring Unavailable" % (self.sensor.name)
        self.message = "Please check %s at %s, temperature monitoring is currently down. Internet or device issue." % (self.sensor.name, self.sensor.zone.name)

    # Sensor temperature is now within threshold checks or has come back online.
    def recovered(self):
        self.subject = "%s Temperature is OK - %s 'F" % (self.sensor.name, self.sensor_data.value_f())
        self.message = "Temperature of %s at %s appears to have recovered, now reporting %s 'F." % (self.sensor.name, self.sensor.zone.name, self.sensor_data.value_f())

    # Obtain the list of all emails that this alert should be delivered to.
    def setup(self):
        self.recipients = []
        users = self.sensor.get_alert_users()
        for user in users:
            if user.email:
                self.recipients.append(user.email)

    """
    # Deliver a multi-part text/HTML email using the django template framework to render the parts of the email.
    # In the future we may want to BCC contacts or send separate emails to each individual to provide
    # some kind of privacy if that becomes necessary.
    """
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

        alert = SensorAlert()
        alert.sensor = self.sensor
        alert.data_point = self.sensor_data
        alert.alert_type = self.alert_type
        alert.alert_class = self.__class__.__name__
        alert.recipients = ", ".join(self.recipients)
        alert.message = self.subject
        alert.save()
        alert.users = self.sensor.get_alert_users()
        alert.save()


