from django import forms
from django.utils.safestring import mark_safe

from anti_spam.utils import get_anticaptcha_token

class AntiCaptchaWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None):
        output = '''
        <script>
        document.write('<input type="hidden" name="anticaptcha" value="%s"/>')
        </script>
        ''' % get_anticaptcha_token()
        return mark_safe(output)
