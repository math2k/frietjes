from django.forms import ModelForm, Select, HiddenInput, TextInput, Textarea, Field, CharField, ModelChoiceField
from app.models import UserOrderItem, UserOrder, MenuItem


class OrderForm(ModelForm):

    def __init__(self, *args, **kwargs):
        if 'provider' in kwargs:
            provider = kwargs.pop('provider')
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
