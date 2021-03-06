from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Email",}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Full Name",}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Password",}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Password Confirmation",}))

    class Meta:
        model = User
        fields = ("email", "full_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("email", "password", "full_name", "is_active", "is_admin")
        

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Email",}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Password",}))


class EditProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control rounded-0 mb-3"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control rounded-0 mb-3"}))

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

    class Meta:
        model = User
        fields = ("full_name", "image",)

class PasswordChangeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Email"}))


class GetRestPasswordForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Password",}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control rounded-0","id": "floatingInput","placeholder": "Password Confirmation",}))

    class Meta:
        model = User
        fields = ("password1", "password2",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user