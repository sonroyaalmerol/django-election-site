from electionadmin.models import Setting
from django.core.exceptions import ObjectDoesNotExist

try:
    started = Setting.objects.get(name="started")
except ObjectDoesNotExist:
    started = Setting(name="started", value="0")
    started.save()
