# widgets.py

from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.urls import reverse


class CustomForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def render(self, name, value, attrs=None, renderer=None):
        extra_attrs = {'data-href': reverse('admin:your_app_model_changelist')}
        if attrs:
            extra_attrs.update(attrs)
        return super().render(name, value, extra_attrs, renderer)


class CustomForeignKeyRawIdFormField(forms.ModelChoiceField):
    widget = CustomForeignKeyRawIdWidget

    def __init__(self, queryset, **kwargs):
        self.model = queryset.model
        super().__init__(queryset, **kwargs)

    def clean(self, value):
        return super().clean(value)
