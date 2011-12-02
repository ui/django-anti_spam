from django import forms
from django.utils.translation import ugettext_lazy as _

from anti_spam.utils import get_anticaptcha_token
from anti_spam.widgets import AntiCaptchaWidget


ERROR_MESSAGE = _(u'You need to enable JavaScript to complete this form.')

class AntiCaptchaField(forms.CharField):
    # This is an anti spam validation technique inspired by
    # http://blog.fili.nl/articles/the-anti-captcha-challenge/
    widget = AntiCaptchaWidget
    default_error_messages = {
        'required': ERROR_MESSAGE,
    }

    def clean(self, value):
    	value = super(AntiCaptchaField, self).clean(value)
    	if value != get_anticaptcha_token():
    		raise forms.ValidationError(ERROR_MESSAGE)
    
