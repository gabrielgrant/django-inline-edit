# Copyright (c) 2010, Stanislas Guerra.
# All rights reserved.
# This document is licensed as free software under the terms of the
# BSD License: http://www.opensource.org/licenses/bsd-license.php


from django.forms.models import ModelFormMetaclass


class ModelFormOptions(object):
    def __init__(self, options=None):
        self.inlines = getattr(options, 'inlines', {}) 

class ModelFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super(ModelFormMetaclass, cls).__new__(cls, name, bases, attrs)
        new_class._forms = ModelFormOptions(getattr(new_class, 'Forms', None))
        return new_class

class ModelForm(forms.ModelForm):
    """
    Add to ModelForm the ability to declare inline formsets.

    It save you from the boiler-plate implementation of cross validation/saving of such 
    forms in the views.
    You should use It in the admin's forms if you need the inherit them in your apps 
    because there is not multi-inherance.

    >>> class Program(models.Model):
    ...     name = models.CharField(max_length=100, blank=True)

    >>> class ImageProgram(models.Model):
    ...     image = models.ImageField('image')
    ...     program = models.ForeignKey(Programm)
    
    >>> class Ringtone(models.Model):
    ...     sound = models.FileField('sound')
    ...     program = models.ForeignKey(Programm)

    Use It in your admin.py instead of django.forms.ModelForm:
    >>> class ProgramAdminForm(ModelForm):
    ... class Meta:
    ...     model = Program
    ...     def clean(self):
    ...         cleaned_data = self.cleaned_data
    ...         # stuff
    ...         return cleaned_data

    In your app, say you declare the following inline formsets:
    >>> ImageProgramFormSet = inlineformset_factory(Program, ImageProgram, 
    ...                                             form=ImageProgramForm, max_num=6)
    >>> RingToneFormSet = inlineformset_factory(Program, RingTone, form=RingtoneProgramForm)

    You can bind them in your program's form:
    >>> class MyProgramForm(ProgramAdminForm):
    ...     class Forms:
    ...         inlines = {
    ...             'images': ImageProgramFormSet,
    ...             'ringtones': RingToneFormSet,
    ...         }

    And instanciate It:
    >>> program_form = MyProgramForm(request.POST, request.FILES, prefix='prog')

    In the template, you access the inlines like that :
    {{ program_form.inlineformsets.images.management_form }}
    {{ program_form.inlineformsets.images.non_form_errors }}
    <table>
    {{ program_form.inlineformsets.images.as_table }}
    </table>
    """

    __metaclass__ = ModelFormMetaclass

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        if hasattr(self._forms, 'inlines'):
            self.inlineformsets = {}
            for key, FormSet in self._forms.inlines.items():
                self.inlineformsets[key] = FormSet(self.data or None, self.files or None,
                                                   prefix=self._get_formset_prefix(key),
                                                   instance=self.instance)

    def save(self, *args, **kwargs):
        instance = super(ModelForm, self).save(*args, **kwargs)
        if hasattr(self._forms, 'inlines'):
            for key, FormSet in self._forms.inlines.items():
                fset = FormSet(self.data, self.files, prefix=self._get_formset_prefix(key),
                               instance=instance)
                fset.save()
        return instance

    def has_changed(self, *args, **kwargs):
        has_changed = super(ModelForm, self).has_changed(*args, **kwargs)
        if has_changed:
            return True
        else:
            for fset in self.inlineformsets.values():
                for i in range(0, fset.total_form_count()):
                    form = fset.forms[i]
                    if form.has_changed():
                        return True
        return False

    def _get_formset_prefix(self, key):
        return u'%s_%s' % (self.prefix, key.upper())

    def _clean_form(self):
        super(ModelForm, self)._clean_form()
        for key, fset in self.inlineformsets.items():
            for i in range(0, fset.total_form_count()):
                f = fset.forms[i]
                if f.errors:
                    self._errors['_%s_%d' %(fset.prefix, i)] = f.non_field_errors