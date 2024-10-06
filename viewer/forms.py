from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.forms import CharField, Textarea, ModelForm
from viewer.models import Profile, Television
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

    biography = CharField(
        label='Tell us your story with movies', widget=Textarea, min_length=40
    )

    @atomic
    def save(self, commit=True):
        # self.instance.is_active = False
        result = super().save(commit)
        biography = self.cleaned_data['biography']
        profile = Profile(biography=biography, user=result)
        if commit:
            profile.save()
        return result


class TVForm(ModelForm):
  class Meta:
    model = Television
    fields = '__all__'