from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'displayname', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = ""
        self.fields['displayname'].label = ""
        self.fields['displayname'].widget.attrs.update({
            'placeholder': 'Add name', 
            'class': 'form-control',
        })
        self.fields['bio'].label = ""
        self.fields['bio'].widget.attrs.update({
            'placeholder': 'Add bio', 
            'class': 'bio form-control',
        })

