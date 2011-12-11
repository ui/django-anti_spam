Django Anti Spam
================

Django Anti Spam is a small library implementing a few anti spam techniques for Django forms. The anti spam techniques implemented in this library aims to user friendly (i.e as transparent as possible to users), so CAPTCHA is not one of them.

If you're looking for CAPTCHA based anti spam solutions for Django forms, there are a few alternatives:

* Django Recaptcha Works: https://bitbucket.org/gnotaras/django-recaptcha-works
* Django Puzzle Captcha: https://puzzlecaptcha.apprabbit.com/
* Django Simple Captcha: http://code.google.com/p/django-simple-captcha/

Installation
============

Simply add `anti_spam` folder to your Python Path, installation via pip is planned.

Using Anti Captcha
==================

The anti captcha of fighting spam technique is described in detail here: http://blog.fili.nl/articles/the-anti-captcha-challenge/ . The technique implemented in this library is similar. You can add anti captcha capability to any form you want simply by decorating your form.::

    from django import forms
    from anti_spam.decorators import anticaptcha


    @anticaptcha
    class MyContactForm(forms.Form):
        ...


Using Akismet
=============

To add Akismet spam checking to your form you will need to:

#. Get a Wordpress API key from `wordpress.com <http://wordpress.com>`_ and add it to a variable called `AKISMET_API_KEY` in settings.py: ::

    AKISMET_API_KEY = 'key_here' 

#. Decorate your form class and tell it which fields to check for spam: ::
    
    @akismet(fields=['body'])
    class ContactForm(forms.Form):
        email = forms.EmailField()
        body = forms.CharField(widget=forms.Textarea()) 

#. Add a `request` argument to form instantiation. So if you previously had ::

    form = ContactForm(request.POST)

 Replace it with: ::

    form = ContactForm(request.POST, request=request)

Coming Soon
===========

* Tests
* Support for `TypePad AntiSpam <http://antispam.typepad.com/>`_
* Installation via `pip`