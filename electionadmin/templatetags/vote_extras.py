from django import template
from electionsite.settings import SECRET_KEY
import hashlib
from django.contrib.sites.models import Site

register = template.Library()

@register.simple_tag
def current_domain():
    return Site.objects.get_current().domain

@register.filter
def getpassword(value):
    """Removes all values of arg from the given string"""
    hashed = "%s%s" % (value, SECRET_KEY)
    hasher = hashlib.md5()
    hasher.update(hashed)
    return hasher.hexdigest()[-8:]
