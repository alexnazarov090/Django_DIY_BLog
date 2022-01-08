from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label="First Name", required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, label="Last Name", required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, label="Email", required=True, help_text='Required. Inform a valid email address.')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, widgets.HiddenInput):
                label = field.label
                attrs = {}
                if isinstance(field.widget, (widgets.Input, widgets.Textarea)) and label:
                    attrs["placeholder"] = label
                if field.required:
                    attrs["required"] = "required"
                field.widget.attrs.update(attrs)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
