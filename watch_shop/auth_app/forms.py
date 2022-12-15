from django import forms
from django.contrib.auth import forms as auth_forms, views as auth_views, login, get_user_model
from django.contrib.auth.forms import UsernameField

from watch_shop.auth_app.models import Profile

UserModel = get_user_model()


class SignUpForm(auth_forms.UserCreationForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    age = forms.IntegerField(required=False)

    class Meta:
        model = UserModel
        fields = (UserModel.USERNAME_FIELD, 'password1', 'password2',)
        field_classes = {'username': auth_forms.UsernameField}

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile = Profile(
            user=user,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            age=self.cleaned_data['age'],
        )
        if commit:
            profile.save()

        return user


class UserEditForm(auth_forms.UserChangeForm):
    class Meta:
        model = UserModel
        fields = '__all__'
        field_classes = {'username': UsernameField}
