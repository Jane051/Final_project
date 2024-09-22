from django.contrib.auth.forms import UserCreationForm
from django.forms import CharField, Textarea
from viewer.models import Profile
from django.db.transaction import atomic


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
