from django.db.models.signals import pre_save
from django.dispatch import receiver
from sensors.models import Zone
import uuid

"""
Automatically set API key for new zones before they are saved to the database.
"""

@receiver(pre_save, sender=Zone)
def zone_set_api_key(sender, instance, *args, **kwargs):
	# Set API key to something like '0172ZD9A1ASF4414B88D6b9A6FEB91EB'
	if instance.pk is None:
		instance.key = str(uuid.uuid4()).replace("-","").upper()