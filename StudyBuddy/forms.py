# from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm
from django import forms
from django.forms import ModelForm
from .models import Account, StudySession


class CustomSignupForm(SignupForm, ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'year', 'major', 'minor']

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        account = Account(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            year=self.cleaned_data['year'],
            major=self.cleaned_data['major'],
            minor=self.cleaned_data['minor'])
        user.save()
        account.save()
        return user


class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)


class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000)


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class StudySessionForm(ModelForm):
    class Meta:
        model = StudySession
        fields = ['topic', 'members', 'date', 'time', 'course']
        widgets = {
            'date': DateInput(),
            'time': TimeInput(format='%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        account = Account.objects.get(pk=self.request.user.username)

        super(StudySessionForm, self).__init__(*args, **kwargs)             
        self.fields['course'].disabled = True
        self.fields['members'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['members'].queryset = account.friends.all()
