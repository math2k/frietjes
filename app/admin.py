from django.contrib.admin import ModelAdmin
from app.models import *
from django.contrib import admin

class UserOrderAdmin(ModelAdmin):
    list_display = ('name', 'order', 'total', 'paid')
    list_filter = ('name',)

class MenuItemAdmin(ModelAdmin):
    list_display = ('name', 'unit_price', 'category', 'provider')
    list_filter = ('category', 'category__provider')

class MenuItemCategoryAdmin(ModelAdmin):
    list_display = ('name', 'provider')
    list_filter = ('provider',)

class OrderAdmin(ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_person":
            r_parts = request.path.split('/')
            order_id = r_parts[-2]
            try:
              kwargs["queryset"] = UserOrder.objects.filter(order=order_id)
            except ValueError:
              pass
        return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Order, OrderAdmin)
admin.site.register(UserOrder, UserOrderAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(MenuItemCategory, MenuItemCategoryAdmin)
admin.site.register(UserOrderItem)
admin.site.register(FoodProvider)
