from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from viewer.models import Profile, Television, MobilePhone, Order
from django.db.transaction import atomic


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


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class TVForm(forms.ModelForm):
    class Meta:
        model = Television
        fields = '__all__'


class MobileForm(forms.ModelForm):
    class Meta:
        model = MobilePhone
        fields = '__all__'


class OrderForm(forms.ModelForm):
    """
    Moznost zaskrtavani (checkbox) policka na preneseni  udaju z profilu do objednavky. Nastaveno, ze zaskrtnuti neni
    povinne a label zobrazi popis pro uzivatele.
    """
    use_profile_data = forms.BooleanField(required=False, label='Použít údaje z profilu.')

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'address', 'city', 'zip_code', 'phone_number',
                  'use_profile_data']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OrderForm, self).__init__(*args, **kwargs)

        if self.user.is_authenticated:
            profile = self.user.profile
            self.fields['first_name'].initial = profile.first_name
            self.fields['last_name'].initial = profile.last_name
            self.fields['address'].initial = profile.address
            self.fields['city'].initial = profile.city
            self.fields['zip_code'].initial = profile.zip_code
            self.fields['phone_number'].initial = profile.phone_number

    def save(self, commit=True):
        order = super(OrderForm, self).save(commit=False)
        if self.cleaned_data['use_profile_data']:
            profile = self.user.profile
            order.first_name = profile.first_name
            order.last_name = profile.last_name
            order.address = profile.address
            order.city = profile.city
            order.zip_code = profile.zip_code
            order.phone_number = profile.phone_number

        if commit:
            order.save()
        return order
