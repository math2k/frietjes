from django.contrib.admin import ModelAdmin
from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserOrderAdmin(ModelAdmin):
    list_display = ('user', 'order', 'total', 'paid')
    list_filter = ('user__username',)


class MenuItemAdmin(ModelAdmin):
    list_display = ('name', 'unit_price', 'category', 'provider')
    list_filter = ('category', 'category__provider')


class MenuItemCategoryAdmin(ModelAdmin):
    list_display = ('name', 'provider')
    list_filter = ('provider',)


class NotificationRequestAdmin(ModelAdmin):
    list_display = ('user', 'selected_providers')


class FeedEntryAdmin(ModelAdmin):
    list_display = ('datetime', 'event')


class OrderAdmin(ModelAdmin):
    list_display = ('company', 'date', 'manager', 'open')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_person":
            r_parts = request.path.split('/')
            order_id = r_parts[-2]
            try:
                kwargs["queryset"] = UserOrder.objects.filter(order=order_id)
            except ValueError:
                pass
        return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class MenuImageInline(admin.StackedInline):
    model = MenuImage


class FoodProviderAdmin(admin.ModelAdmin):

    inlines = [
        MenuImageInline
    ]


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class UserInviteAdmin(admin.ModelAdmin):
    list_display = ['email', 'company', 'used_on']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(UserInvite, UserInviteAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserOrder, UserOrderAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(MenuItemCategory, MenuItemCategoryAdmin)
admin.site.register(UserOrderItem)
admin.site.register(FoodProvider, FoodProviderAdmin)
admin.site.register(NotificationRequest, NotificationRequestAdmin)
admin.site.register(FeedEntry, FeedEntryAdmin)
