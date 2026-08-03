from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import Product


class PasswordInput(forms.PasswordInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs.setdefault('class', 'form-control')
        attrs['class'] = f"{attrs['class']} password-input".strip()
        attrs['style'] = f"padding-right: 42px; {attrs.get('style', '')}".strip()
        attrs['id'] = attrs.get('id', name)
        input_html = super().render(name, value, attrs=attrs, renderer=renderer)
        toggle_id = f"{attrs['id']}_toggle"
        return format_html(
            '<div class="password-toggle-wrapper" style="position: relative; width: 100%;">{}<button type="button" class="btn btn-link p-0" data-password-toggle="{}" id="{}" aria-label="Mostrar senha" style="position: absolute; top: 50%; right: 8px; transform: translateY(-50%); border: 0; background: transparent; color: #6c757d; padding: 0 6px; z-index: 2;"><i data-lucide="eye-off"></i></button></div>',
            input_html,
            attrs['id'],
            toggle_id,
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'brand', 'company']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
        }


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Senha', widget=PasswordInput())

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = User.objects.filter(email__iexact=email).first()
            if user:
                user = authenticate(username=user.username, password=password)
            else:
                user = None

            if user is None:
                raise forms.ValidationError('E-mail ou senha inválidos.')

            self.user_cache = user

        return cleaned_data


class RegisterForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Senha', widget=PasswordInput())
    password_confirm = forms.CharField(label='Confirmar senha', widget=PasswordInput())

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem.')

        return cleaned_data
