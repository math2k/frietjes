from django.contrib.admin import ModelAdmin
from app.models import *
from django.contrib import admin

class UserOrderAdmin(ModelAdmin):
    list_display = ('name', 'order', 'total', 'paid')

admin.site.register(Order)
admin.site.register(UserOrder, UserOrderAdmin)
admin.site.register(MenuItem)
admin.site.register(MenuItemCategory)
admin.site.register(UserOrderItem)
