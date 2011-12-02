from django.conf import settings
from django.utils.hashcompat import md5_constructor

def get_anticaptcha_token():
	# The purpose of this anticaptcha token is just to generate
	# a random value so we simply hash something that's always
	# available, but different in most django installs
	return md5_constructor(settings.MEDIA_ROOT).hexdigest()