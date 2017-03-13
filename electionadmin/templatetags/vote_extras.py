from django import template
from electionsite.settings import SECRET_KEY
import hashlib

register = template.Library()

@register.filter
def getpassword(value):
    """Removes all values of arg from the given string"""
    hashed = "%s%s" % (value, SECRET_KEY)
    hasher = hashlib.md5()
    hasher.update(hashed)
    return hasher.hexdigest()[-8:]
