from django.forms import ModelForm, Select, HiddenInput, TextInput, Textarea, Field, CharField
from app.models import UserOrderItem, UserOrder


class OrderForm(ModelForm):
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
