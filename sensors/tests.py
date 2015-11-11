from django.test import TestCase
from sensors.models import Zone, Sensor, SensorData
from notifications.models import SensorAlertGroup, SensorAlert
from django.contrib.auth.models import User
from django.core import mail

class SensorDataTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="testing@rpnutrients.com", password="whoa")
        
        self.alert_group = SensorAlertGroup.objects.create(name="Test Alert Group")
        self.alert_group.users.add(self.user)

        self.zone = Zone.objects.create(name="Testing Zone")
        
        self.sensor = Sensor.objects.create(
            name = "Testing Sensor",
            guid = "012345678910TEST",
            min_value = 10.0,
            min_value_operator = ">",
            max_value = 20.0,
            max_value_operator = "<",
            zone = self.zone,
        )
        self.sensor.alert_groups.add(self.alert_group)


    def test_sensor_data_alerts_emails(self):
        # Inbox should be empty
        self.assertEqual(len(mail.outbox), 0)


        # This test will pass the threshold checks, no alerts sent
        data = SensorData.objects.create(sensor=self.sensor, value=15.0)

        # Sensor state should be true
        # Sensor should not be down
        # Data state should be true
        # Data state change should be false
        self.assertEqual(self.sensor.state, True)
        self.assertEqual(self.sensor.down, False)
        self.assertEqual(data.state, True)
        self.assertEqual(data.state_changed, False)

        # No emails in our inbox at this point
        self.assertEqual(len(mail.outbox), 0)


        # Sensor low, triggers "alert" email
        data = SensorData.objects.create(sensor=self.sensor, value=5.0)

        # Sensor state should be false
        # Sensor should not be down
        # Data state should be false
        # Data state change should be true
        self.assertEqual(self.sensor.state, False)
        self.assertEqual(self.sensor.down, False)
        self.assertEqual(data.state, False)
        self.assertEqual(data.state_changed, True)

        # A sensor alert should have been created
        alert = SensorAlert.objects.get(data_point=data)
        self.assertEqual(self.sensor, alert.sensor)
        self.assertEqual(alert.alert_type, "alert")
        self.assertEqual(alert.alert_class, "Email")
        self.assertEqual(alert.recipients, self.user.email)
        self.assertTrue("Alert" in alert.message)

        # One email in the box now
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue("Alert" in mail.outbox[0].subject)


        # Sensor normal, triggers "recovered" email
        data = SensorData.objects.create(sensor=self.sensor, value=15.0)

        # A sensor alert should have been created
        alert = SensorAlert.objects.get(data_point=data)
        self.assertEqual(self.sensor, alert.sensor)
        self.assertEqual(alert.alert_type, "recovered")
        self.assertEqual(alert.alert_class, "Email")
        self.assertEqual(alert.recipients, self.user.email)
        self.assertTrue("OK" in alert.message)

        # One email in the box now
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue("OK" in mail.outbox[1].subject)





