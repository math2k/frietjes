from django.contrib.admin import ModelAdmin
from app.models import *
from django.contrib import admin

class UserOrderAdmin(ModelAdmin):
    list_display = ('name', 'order', 'total', 'paid')

class OrderAdmin(ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_person":
            r_parts = request.path.split('/')
            order_id = r_parts[-2]
            kwargs["queryset"] = UserOrder.objects.filter(order=order_id)
        return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Order, OrderAdmin)
admin.site.register(UserOrder, UserOrderAdmin)
admin.site.register(MenuItem)
admin.site.register(MenuItemCategory)
admin.site.register(UserOrderItem)
