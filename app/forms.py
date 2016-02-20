from django import forms
from django.forms import ModelForm, Select, HiddenInput, TextInput, Textarea, Field, CharField, ModelChoiceField
from app.models import UserOrderItem, UserOrder, MenuItem, FoodProvider, NotificationRequest


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

    notes = CharField(required=False, widget=Textarea(attrs={'placeholder': 'Notes ?'}))

    class Meta:
        model = UserOrder
        exclude = []

        widgets = {
            'order': HiddenInput(),
            'name': TextInput(attrs={'placeholder': 'Name'})
        }


class NotificationRequestForm(ModelForm):

    providers = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=FoodProvider.objects.all())

    class Meta:
        model = NotificationRequest
        exclude = []
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Name', 'style': 'width: 50%'}),
            'email': TextInput(attrs={'placeholder': 'Email address', 'style': 'width: 50%'})
        }


class ImportMenuItemsForm(forms.Form):
    csv = forms.CharField(widget=forms.Textarea())