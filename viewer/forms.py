from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.forms import CharField, Textarea, ModelForm
from viewer.models import Profile, Television
from django.db.transaction import atomic
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import re


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    # Overriding field labels
    old_password = forms.CharField(label=_("Staré heslo"), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("Nové heslo"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Potvrďte nové heslo"), widget=forms.PasswordInput)

    # Overriding the error messages
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Hesla se neshodují. Zkuste to znovu."))
        return password2


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label=_('Uživatelské jméno'),
        min_length=3,
        max_length=20,
        help_text=_('Toto pole je povinné. Uživatelské jméno musí být jediněčné, obsahovat minimálně 3 a maximálně 20 znaků, '
                    'pouze písmena, číslice a @/./+/-/_ znaky.')
    )
    first_name = forms.CharField(label=_('Jméno'), required=False,)
    last_name = forms.CharField(label=_('Příjmení'), required=False,)
    email = forms.EmailField(
        label=_('Email'), required=True,
        help_text=_('Zadejte prosím platný e-mail.'),
    )
    password1 = forms.CharField(
        label=_('Heslo'),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_('Vaše heslo musí obsahovat alespoň 8 znaků.')
    )
    password2 = forms.CharField(
        label=_('Heslo znovu'),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_('Prosím, zadejte stejné heslo pro ověření.')
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Uživatelské jméno je již použito. Zvolte jiné.'))
        if len(username) > 20:
            raise forms.ValidationError(_('Uživatelské jméno nesmí být delší než 30 znaků.'))
        if len(username) < 3:
            raise forms.ValidationError(_('Uživatelské jméno nesmí být kratší než 2 znaky.'))

        # Vlastní regulární výraz pro kontrolu platnosti uživatelského jména
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError(
                _('Uživatelské jméno může obsahovat pouze písmena, číslice, a znaky @/./+/-/_.'))

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Zkontroluje, zda je e-mail v platném formátu
        if email and not forms.EmailField().clean(email):
            raise forms.ValidationError(_('Zadejte prosím platný e-mail.'))

        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    @atomic
    def save(self, commit=True):
        # self.instance.is_active = False
        result = super().save(commit)
        profile = Profile(user=result)
        if commit:
            profile.save()
        return result


class TVForm(ModelForm):
    class Meta:
        model = Television
        fields = '__all__'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'city', 'zipcode', 'avatar',
                  'communication_channel']
        labels = {
            'first_name': _('Jméno'),
            'last_name': _('Příjmení'),
            'phone_number': _('Telefon'),
            'address': _('Adresa'),
            'city': _('Město'),
            'zipcode': _('PSČ'),
            'avatar': _('Profilový obrázek'),
            'communication_channel': _('Komunikační kanál'),
        }
