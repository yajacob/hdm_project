from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

# UserCreationForm class inheritance to add email, firstname, and lastname
class HDMUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )        

    # overriding for save method
    def save(self, commit = True):
        user = super(HDMUserCreationForm, self).save(commit = False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    