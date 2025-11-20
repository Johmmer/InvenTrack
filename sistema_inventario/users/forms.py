from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'input-dark', 'placeholder': 'Correo electrónico'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-dark', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-dark', 'placeholder': 'Apellido'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # apply input-dark class to default fields
        for field_name in ['username', 'password1', 'password2']:
            field = self.fields.get(field_name)
            if field:
                existing_attrs = field.widget.attrs
                existing_attrs.update({'class': 'input-dark'})