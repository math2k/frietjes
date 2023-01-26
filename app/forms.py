from django import forms
from django.forms import ModelForm, Select, HiddenInput, TextInput, Textarea, Field, CharField, ModelChoiceField, \
    EmailField, widgets
from django.views.generic import CreateView
from django_registration.forms import RegistrationForm

from app.models import UserOrderItem, UserOrder, MenuItem, FoodProvider, NotificationRequest, UserInvite, Order


class OrderForm(ModelForm):

    def __init__(self, *args, **kwargs):
        if 'provider' in kwargs:
            provider = kwargs.pop('provider')
        else:
            provider = None
        super(OrderForm, self).__init__(*args, **kwargs)
        if provider:
            self.fields['menu_item'].queryset = MenuItem.objects.filter(category__provider=provider)

    class Meta:
        model = UserOrderItem
        exclude = ['user_order']


class UserOrderForm(ModelForm):

    notes = CharField(required=False, widget=Textarea(attrs={'placeholder': 'Notes ?', 'rows': 2}))

    class Meta:
        model = UserOrder
        exclude = ['user']

        widgets = {
            'order': HiddenInput()
        }


class NewUserOrderForm(ModelForm):

    notes = CharField(required=False, widget=Textarea(attrs={'placeholder': 'Notes ?'}))
    items = CharField(required=True, widget=HiddenInput)

    class Meta:
        model = UserOrder
        exclude = ['user']

        widgets = {
            'order': HiddenInput()
        }


class NotificationRequestForm(ModelForm):

    providers = forms.ModelMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, queryset=FoodProvider.objects.all())

    class Meta:
        model = NotificationRequest
        exclude = ['user', 'email']


class ImportMenuItemsForm(forms.Form):
    csv = forms.CharField(widget=forms.Textarea())


class FrietjesRegistrationForm(RegistrationForm):
    secret = forms.CharField(widget=HiddenInput)


class UserInviteForm(ModelForm):
    email = EmailField(label='', required=True, widget=widgets.TextInput(attrs={'placeholder': 'john@doe.com'}))

    class Meta:
        model = UserInvite
        exclude = ['secret', 'used_on', 'company']
