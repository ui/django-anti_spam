from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from anti_spam.fields import AntiCaptchaField


def anticaptcha(cls):
    """
    Applies anti captcha spam validation.
    Check http://blog.fili.nl/articles/the-anti-captcha-challenge/
    for more details on how this technique works
    
    Example:

	from anti_spam.decorators import anticaptcha

    @anticaptcha
	class ContactForm(forms.Form):
        email = forms.EmailField()
        body = forms.CharField(widget=forms.Textarea())

    """
    old_init = cls.__init__
    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        self.fields['anticaptcha'] = AntiCaptchaField(label='')
    cls.__init__ = new_init
    return cls


def enhance_clean_function(cls, fields):
    cls._original_clean = getattr(cls, 'clean')

    # Add akismet cleaning to form's clean method
    def clean(self):
        cleaned_data = self._original_clean()
        if not self.errors:
            API_KEY = getattr(settings, 'AKISMET_API_KEY', '')
            if not API_KEY:
                raise ImproperlyConfigured(
                    "The AKISMET_API_KEY setting must be set.")
            
            from akismet import Akismet
            from django.contrib.sites.models import Site
            api = Akismet(key=API_KEY, blog_url='http://%s/' %
                                           Site.objects.get_current().domain)
            if api.verify_key():
                akismet_data = {
                    'comment_type': 'comment',
                    'referer': self.request.META.get('HTTP_REFERER', ''),
                    'user_ip': self.request.META.get('REMOTE_ADDR', ''),
                    'user_agent': self.request.META.get('HTTP_USER_AGENT', '')
                }
                
                for field_name in fields:
                    value = smart_str(cleaned_data.get(field_name, ''))
                    if value and api.comment_check(value, data=akismet_data):
                        error_msg = _("Akismet thinks this field is spam")
                        self._errors[field_name] = self.error_class([error_msg])
        return cleaned_data
    
    setattr(cls, 'clean', clean)


def store_request_data(cls, pop_request=True):
    # Strip request kwarg and store it on the form instance.
    # This request object will be used later when cleaning the form.
    orig_init = cls.__init__
    
    def __init__(self, *args, **kwargs):
        if not 'request' in kwargs and not hasattr(self, 'request'):
            raise TypeError("Keyword argument 'request' must be supplied")
        self.request = kwargs.pop('request') if pop_request else kwargs['request']
        orig_init(self, *args, **kwargs)
    
    cls.__init__ = __init__
    return cls


class akismet(object):
    """
    Submit field content to Akismet for spam validation during form.clean().

    Example:

    from anti_spam.decorators import akismet

    @akismet(fields=['body'])
    class ContactForm(forms.Form):
        email = forms.EmailField()
        body = forms.CharField(widget=forms.Textarea())
    """
    
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, cls):
        self.actual_decorator(cls)
        return cls
        
    def actual_decorator(self, cls):
        store_request_data(cls)
        enhance_clean_function(cls, self.fields)


def check_cookies(cls, names):
    cls._original_clean = getattr(cls, 'clean')
    # Check if request has specified cookies or raise a validation error
    def clean(self):
        cleaned_data = self._original_clean()
        if not self.errors:
            for name in names:
                if not name in self.request.COOKIES:
                    error_msg = _('You must enable cookies to complete this form.')
                    raise forms.ValidationError(error_msg)
        return cleaned_data
    
    setattr(cls, 'clean', clean)


class require_cookies(object):
    """
    Form that requires cookies to be enabled to pass validation.
    Note that this may prevent browsers that don't support cookies
    from submitting the form. In such an event, an appropriate error 
    message will be displayed.

    Example:

    from anti_spam.decorators import require_cookies

    @require_cookies(names=['sessionid'])
    class ContactForm(forms.Form):
        email = forms.EmailField()
        body = forms.CharField(widget=forms.Textarea())
    """
    
    def __init__(self, names, pop_request=True):
        self.names = names
        self.pop_request = pop_request

    def __call__(self, cls):
        self.actual_decorator(cls)
        return cls
        
    def actual_decorator(self, cls):
        store_request_data(cls, self.pop_request)
        check_cookies(cls, self.names)
