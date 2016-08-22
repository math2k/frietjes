# -*- coding: utf-8 -*-
import csv
import datetime
import random
import uuid

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms import formset_factory, Select
from django.forms.models import modelformset_factory
from django.http import Http404
from django.utils.decorators import method_decorator
from registration.backends.simple.views import RegistrationView, User

from app.forms import OrderForm, UserOrderForm, UserOrder, NotificationRequestForm, ImportMenuItemsForm, \
    FrietjesRegistrationForm, UserInviteForm
from app.models import Order, MenuItem, UserOrderItem, NotificationRequest, MenuItemCategory, UserProfile, FoodProvider, \
    EatingGroup, EatingGroupMember
from django.views.generic import (
    TemplateView, FormView, View, RedirectView, CreateView, UpdateView, DetailView, ListView, DeleteView)
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from app.signals import *


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['view_passed'] = self.request.GET.get('past')
        if self.request.user.is_authenticated():
            if ctx['view_passed']:
                if self.request.GET.get('all'):
                    ctx['all_orders'] = Order.objects.filter(company=self.request.user.profile.company).order_by("-pk").prefetch_related('provider', 'delivery_person')
                    ctx['all_group_outings'] = EatingGroup.objects.filter(company=self.request.user.profile.company).order_by("-pk").prefetch_related('provider')
                else:
                    ctx['all_orders'] = Order.objects.filter(company=self.request.user.profile.company).order_by("-pk").prefetch_related('provider', 'delivery_person')[:5]
                    ctx['all_group_outings'] = EatingGroup.objects.filter(company=self.request.user.profile.company).order_by("-pk").prefetch_related('provider')[:5]
            #ctx['open_order'] = Order.objects.filter(open=True, company=self.request.user.profile.company).order_by("-date").last()
            #ctx['open_group'] = EatingGroup.objects.filter(open=True, company=self.request.user.profile.company).order_by("-date").last()
            ctx['upcoming_groups'] = EatingGroup.objects.filter(open=True, company=self.request.user.profile.company, departing_time__gte=datetime.date.today())
            ctx['upcoming_orders'] = Order.objects.filter(open=True, company=self.request.user.profile.company, delivery_time__gte=datetime.date.today())

        #ctx['feed_entries'] = FeedEntry.objects.filter(datetime__day=datetime.datetime.now().day).order_by('-datetime')[:15]
        #ctx['feed_entries'] = FeedEntry.objects.filter().order_by('-datetime')[:15]
        #ctx['show_notification_tooltip'] = False if self.request.COOKIES.get('show_notification_tooltip') == '0' else True
        #ctx['show_account_tooltip'] = False if self.request.COOKIES.get('show_account_tooltip') == '0' else True
        if self.request.user.is_authenticated():
            ctx['my_orders'] = UserOrder.objects.filter(user=self.request.user).order_by('-order__date').prefetch_related('order')
        else:
            ctx['my_orders'] = []
        if self.request.user.is_authenticated():
            ctx['unpaid_orders'] = UserOrder.objects.filter(user=self.request.user, paid=False, order__open=False)
        ctx['invite_form'] = UserInviteForm()
        return ctx


@method_decorator(login_required, name='dispatch')
class OrderFormView(FormView):
    template_name = "order.html"
    form_class = UserOrderForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        ctx = super(OrderFormView, self).get_context_data(**kwargs)
        ctx['order'] = get_object_or_404(Order, pk=self.kwargs['order'])
        order_form_formset = formset_factory(form=OrderForm, extra=10, min_num=1, validate_min=True)
        # qs = UserOrderItem.objects.filter(menu_item__category__provider__id=ctx['order'].provider.pk)
        if self.request.POST:
            ctx['order_form_formset'] = order_form_formset(self.request.POST,
                                                           form_kwargs={'provider': ctx['order'].provider})
            ctx['user_order'] = UserOrderForm(self.request.POST)
        else:
            ctx['order_form_formset'] = order_form_formset(form_kwargs={'provider': ctx['order'].provider})
            ctx['user_order'] = UserOrderForm(initial={'order': ctx['order'], 'name': self.request.user.username})
        return ctx

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs.get('order'))
        order_form_formset = formset_factory(OrderForm, min_num=1, validate_min=True)
        of_formset_instance = order_form_formset(self.request.POST, form_kwargs={'provider': order.provider})
        if of_formset_instance.is_valid():
            form.instance.user = self.request.user
            form.instance.save()
            for f in of_formset_instance:
                if f.is_valid() and f.instance.menu_item_id is not None:
                    f.instance.user_order = form.instance
                    f.instance.save()
            fe = FeedEntry(event='_{0}_ placed an order at {1}'.format(self.request.user.username, order.provider.name))
            fe.save()
            messages.success(self.request, "Your order has been saved!")
        else:
            form.add_error(None, "You need to select something!")
            return super(OrderFormView, self).form_invalid(form)
        return super(OrderFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(OrderFormView, self).form_invalid(form)


@method_decorator(login_required, name='dispatch')
class CreateUserOrderFormView(FormView):
    template_name = "userorder_form.html"
    form_class = UserOrderForm

    def get_context_data(self, **kwargs):
        ctx = super(CreateUserOrderFormView, self).get_context_data(**kwargs)
        ctx['order'] = get_object_or_404(Order, pk=self.kwargs['order'])
        ctx['menu_items'] = MenuItem.objects.filter(category__provider=ctx['order'].provider).select_related('category').order_by('category__order', 'name')
        if self.request.POST:
            ctx['user_order'] = UserOrderForm(self.request.POST)
        else:
            ctx['user_order'] = UserOrderForm(initial={'order': ctx['order']})
        try:
            ctx['latest_order_items'] = UserOrder.objects.filter(order__provider=ctx['order'].provider, user=self.request.user).order_by('-order__pk')[0].userorderitem_set.all().values_list('menu_item__pk', flat=True)
        except:
            ctx['latest_order_items'] = []
        return ctx

    def form_valid(self, form):
        items = [i for i in self.request.POST.get('items', '').split(',') if i != '']
        if len(items) == 0:
            form.add_error(None, 'No items in cart')
            return self.form_invalid(form)
        form.instance.user = self.request.user
        form.instance.save()
        self.instance = form.instance
        for i in items:
            uoi = UserOrderItem()
            uoi.menu_item_id = i
            uoi.user_order_id = form.instance.pk
            uoi.save()
        return super(CreateUserOrderFormView, self).form_valid(form)

    def get_success_url(self):
        return "{0}?success=1".format(reverse_lazy('user-order-view', kwargs={'user_order': self.instance.pk }))


class TogglePaidFlag(View):
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        uo = get_object_or_404(UserOrder, pk=kwargs.get('uo'))
        if request.user.is_staff or request.user in (uo.order.delivery_person, uo.order.manager):
            uo.paid = not uo.paid
            uo.save()
            messages.success(request, "{0}'s order marked as {1}".format(uo.user.username, "paid" if uo.paid else "not paid"))
            if uo.paid:
                fe = FeedEntry(event='_{0}_ paid their order'.format(uo.user.username))
                fe.save()
            return redirect(request.META.get('HTTP_REFERER'))


class ToggleUserStaffFlag(View):
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            u = get_object_or_404(User, pk=kwargs.get('pk'))
            admin_group = Group.objects.get(name='admin')
            if u.is_staff:
                if len(User.objects.filter(is_staff=True, profile__company=self.request.user.profile.company)) == 1:
                    messages.error(self.request, "Removing admin privileges of that user would make the company admin-less. You don't want that.")
                    return redirect(request.META.get('HTTP_REFERER'))
                u.is_staff = not u.is_staff
                u.save()
                admin_group.user_set.remove(u)
                messages.warning(request, "{0} is not an admin anymore".format(u.username))
            else:
                u.is_staff = not u.is_staff
                u.save()
                admin_group.user_set.add(u)
                messages.success(request, "{0} is now an admin".format(u.username))
            return redirect(request.META.get('HTTP_REFERER'))


class SetOrderDeliveredView(View):
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            o = get_object_or_404(Order, pk=kwargs.get('pk'))
            o.delivered = True
            o.save()
            messages.success(request, "Order has been marked as delivered!")
            return redirect(request.META.get('HTTP_REFERER'))


class Redirect(RedirectView):
    pattern_name = "home"

    def get_redirect_url(self, *args, **kwargs):
        messages.success(self.request,
                         "Check this out! We have moved to a more appropriate .eu domain: 4lunch.eu, woohoo!")
        return super(Redirect, self).get_redirect_url(*args, **kwargs)


class PickRandomDeliveryPerson(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            o = get_object_or_404(Order, pk=kwargs.get('o'))
            if o.delivery_person:
                messages.error(request, "{0} is already set as the delivery person!".format(o.delivery_person.username))
            else:
                o.assign_random_delivery_person()
                if o.delivery_person:
                    messages.success(request, "{0} has been designated as volunteer! Thanks {0} :D".format(
                        o.delivery_person.username))
                    fe = FeedEntry(event='_{0}_ has been randomly selected to pick up the order from {1}'
                                   .format(o.delivery_person.username, o.provider.name))
                    fe.save()
                else:
                    messages.error(request, "Something went wrong .. do you have orders ?")
        return redirect(request.META.get('HTTP_REFERER'))


class OrderView(TemplateView):
    template_name = "order_view.html"

    def get_context_data(self, **kwargs):
        ctx = super(OrderView, self).get_context_data(**kwargs)
        ctx['order'] = Order.objects.get(pk=kwargs['order'])
        ctx['order_items'] = UserOrderItem.objects.filter(user_order__order=ctx['order']). \
            values('menu_item__name').annotate(count=Count('menu_item__name')).order_by('menu_item__category__order')
        ctx['orders_with_notes'] = UserOrder.objects.filter(order=ctx['order']).exclude(notes__isnull=True).exclude(notes__exact='')
        return ctx


class UserOrderView(TemplateView):
    template_name = "userorder_view.html"

    def get_context_data(self, **kwargs):
        ctx = super(UserOrderView, self).get_context_data(**kwargs)
        ctx['user_order'] = UserOrder.objects.get(pk=kwargs['user_order'])
        ctx['success'] = 'success' in self.request.GET
        return ctx


class UserOrderDeleteView(DeleteView):
    model = UserOrder

    def get_object(self, queryset=None):
        obj = super(UserOrderDeleteView, self).get_object(queryset)
        if self.request.user != obj.user or not obj.order.open:
            raise Http404
        return obj

    def get_success_url(self):
        messages.success(self.request, 'Your order has been deleted!')
        return self.request.META.get('HTTP_REFERER')


@method_decorator(login_required, name='dispatch')
class NotificationRequestFormView(UpdateView):
    form_class = NotificationRequestForm
    model = NotificationRequest
    template_name = 'notificationrequest_form.html'

    def dispatch(self, request, *args, **kwargs):
        res = super(NotificationRequestFormView, self).dispatch(request, *args, **kwargs)
        res.set_cookie('show_notification_tooltip', '0', expires="Fri, 01-Jan-25 12:12:12 GMT")
        return res

    def get_object(self, queryset=None):
        obj, created = NotificationRequest.objects.get_or_create(user=self.request.user)
        return obj

    def form_valid(self, form):
        resp = super(NotificationRequestFormView, self).form_valid(form)
        return resp

    def get_success_url(self):
        if len(self.object.providers.all()) > 0 or self.object.all_providers or self.object.deliveries:
            messages.success(self.request, "Notifications saved!")
        else:
            messages.warning(self.request, "We won't bother you with notifications.")
        return reverse_lazy('home')


@method_decorator(login_required, name='dispatch')
class NotificationCancelFormView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            NotificationRequest.objects.get(secret=self.kwargs['s']).delete()
            messages.success(self.request, "You won't receive any email from us anymore!")
        except:
            messages.error(self.request, "Something went wrong :(")
        return reverse_lazy('home')


@method_decorator(staff_member_required, name='dispatch')
class ImportMenuItemsFormView(FormView):
    form_class = ImportMenuItemsForm
    template_name = "import.html"

    def get_context_data(self, **kwargs):
        ctx = super(ImportMenuItemsFormView, self).get_context_data(**kwargs)
        ctx['categories'] = MenuItemCategory.objects.all().select_related('provider')
        return ctx

    def form_valid(self, form):
        csv_content = form.cleaned_data['csv']
        reader = csv.reader(csv_content.splitlines(), delimiter=";")
        for row in reader:
            mi = MenuItem(name=unicode(row[0]), unit_price=row[1], category_id=row[2])
            mi.save()
            messages.success(self.request, u"Saved {name} at {price}€".format(name=row[0], price=row[1]))

        return super(ImportMenuItemsFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')


class FrietjesRegistrationView(RegistrationView):

    form_class = FrietjesRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.invite = UserInvite.objects.get(pk=self.kwargs['secret'], used_on=None)
        except UserInvite.DoesNotExist:
            messages.error(self.request, 'Invalid invitation link')
            return redirect(reverse_lazy('home'))
        return super(FrietjesRegistrationView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'secret': self.invite.secret, 'email': self.invite.email}

    def form_valid(self, form):
        res = super(FrietjesRegistrationView, self).form_valid(form)
        # TODO: Fix this mess
        user = User.objects.get(username=form.cleaned_data['username'])
        user_profile = UserProfile(user_id=user.pk, company=self.invite.company)
        user_profile.save()
        self.invite.used_on = datetime.datetime.now()
        self.invite.save()
        return res

    def get_success_url(self, user):
        return self.request.GET.get('next', self.request.POST.get('next', reverse_lazy('home')))


class UserInviteFormView(CreateView):
    model = UserInvite
    fields = ['email']
    template_name = 'userinvite_form.html'

    def form_valid(self, form):
        invite = form.save(commit=False)
        invite.company = self.request.user.profile.company
        return super(UserInviteFormView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Invitation sent!')
        return self.request.META.get('HTTP_REFERER')


@method_decorator(staff_member_required, name='dispatch')
class CreateOrderFormView(CreateView):
    model = Order
    template_name = "order_form.html"
    fields = ['open', 'delivered', 'manager', 'provider', 'delivery_person', 'delivery_time', 'closing_time', 'notes', 'silent', 'cancelled', 'cancelled_reason']

    def get_initial(self):
        return {
            'manager': self.request.user
        }

    def get_form(self, form_class=None):
        form = super(CreateOrderFormView, self).get_form(form_class)
        form.fields['provider'].queryset = FoodProvider.objects.filter(type__in=['takeaway']).distinct()
        form.fields['manager'].queryset = User.objects.filter(profile__company=self.request.user.profile.company)
        form.fields['closing_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['closing_time'].widget.format = '%d/%m/%Y %H:%M'
        form.fields['delivery_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['delivery_time'].widget.format = '%d/%m/%Y %H:%M'
        if not form.instance.id:
            # New group order, only current user can be the delivery person
            form.fields['delivery_person'].queryset = User.objects.filter(pk=self.request.user.pk)
        return form

    def form_valid(self, form):
        order = form.save(commit=False)
        order.company = self.request.user.profile.company
        order.manager = self.request.user
        return super(CreateOrderFormView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Group order created')
        return reverse_lazy('home')


@method_decorator(staff_member_required, name='dispatch')
class CreateGroupFormView(CreateView):
    model = EatingGroup
    template_name = "group_form.html"
    fields = ['open', 'provider', 'manager', 'departing_time', 'closing_time', 'notes', 'silent', 'cancelled', 'cancelled_reason']

    def get_initial(self):
        return {
            'manager': self.request.user
        }

    def get_form(self, form_class=None):
        form = super(CreateGroupFormView, self).get_form(form_class)
        form.fields['manager'].queryset = User.objects.filter(profile__company=self.request.user.profile.company)
        form.fields['provider'].queryset = FoodProvider.objects.filter(type__in=['restaurant', 'shop']).distinct()
        form.fields['closing_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['closing_time'].widget.format = '%d/%m/%Y %H:%M'
        form.fields['departing_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['departing_time'].widget.format = '%d/%m/%Y %H:%M'
        return form

    def form_valid(self, form):
        order = form.save(commit=False)
        order.company = self.request.user.profile.company
        order.manager = self.request.user
        return super(CreateGroupFormView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Group outing created')
        return reverse_lazy('home')


@method_decorator(staff_member_required, name='dispatch')
class UpdateGroupFormView(UpdateView):
    model = EatingGroup
    template_name = "group_form.html"
    fields = ['open', 'manager', 'departing_time', 'closing_time', 'notes', 'silent', 'cancelled', 'cancelled_reason']

    def get_form(self, form_class=None):
        form = super(UpdateGroupFormView, self).get_form(form_class)
        form.fields['manager'].queryset = User.objects.filter(profile__company=self.request.user.profile.company)
        form.fields['closing_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['closing_time'].widget.format = '%d/%m/%Y %H:%M'
        form.fields['departing_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['departing_time'].widget.format = '%d/%m/%Y %H:%M'
        return form

    def form_valid(self, form):
        order = form.save(commit=False)
        order.company = self.request.user.profile.company
        return super(UpdateGroupFormView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Group updated')
        return reverse_lazy('home')


@method_decorator(staff_member_required, name='dispatch')
class UpdateOrderFormView(UpdateView):
    model = Order
    template_name = "order_form.html"
    fields = ['open', 'delivered', 'manager', 'delivery_person', 'delivery_time', 'closing_time', 'notes', 'silent', 'cancelled', 'cancelled_reason']

    def get_form(self, form_class=None):
        form = super(UpdateOrderFormView, self).get_form(form_class)
        form.fields['manager'].queryset = User.objects.filter(profile__company=self.request.user.profile.company)
        user_list = [uo.user.id for uo in form.instance.userorder_set.all()]
        user_list.append(self.request.user.id)
        form.fields['delivery_person'].queryset = User.objects.filter(id__in=user_list)
        form.fields['closing_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['closing_time'].widget.format = '%d/%m/%Y %H:%M'
        form.fields['delivery_time'].input_formats = ('%d/%m/%Y %H:%M',)
        form.fields['delivery_time'].widget.format = '%d/%m/%Y %H:%M'
        return form

    def form_valid(self, form):
        order = form.save(commit=False)
        order.company = self.request.user.profile.company
        return super(UpdateOrderFormView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Group order updated')
        return reverse_lazy('home')


class FoodProviderQuickView(DetailView):
    model = FoodProvider
    template_name = "foodprovider_view.html"


@method_decorator(staff_member_required, name='dispatch')
class ListCompanyUsers(ListView):
    model = User
    ordering = 'username'
    template_name = "user_list.html"

    def get_context_data(self, **kwargs):
        ctx = super(ListCompanyUsers, self).get_context_data(**kwargs)
        ctx['invite_form'] = UserInviteForm()
        return ctx

    def get_queryset(self):
        return User.objects.filter(profile__company=self.request.user.profile.company).order_by('username')


@method_decorator(staff_member_required, name='dispatch')
class ListUserOrdersView(ListView):
    model = User
    template_name = "userorder_list.html"

    def get_queryset(self):
        return UserOrder.objects.filter(user_id=self.kwargs.get('pk')).order_by('-order__date')

    def get_context_data(self, **kwargs):
        ctx = super(ListUserOrdersView, self).get_context_data(**kwargs)
        ctx['user'] = User.objects.get(pk=self.kwargs.get('pk'))
        return ctx


@method_decorator(staff_member_required, name='dispatch')
class DeleteUser(DeleteView):
    model = User

    def get_success_url(self):
        messages.success(self.request, 'User has been deleted.')
        return reverse_lazy('user-list')


@method_decorator(login_required, name='dispatch')
class LeaveGroupView(DeleteView):
    model = EatingGroupMember

    def dispatch(self, request, *args, **kwargs):
        membership = EatingGroupMember.objects.get(pk=self.kwargs['pk'])
        if request.user.is_staff or request.user == membership.user:
            return super(LeaveGroupView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(self.request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        messages.success(self.request, 'User has been removed from group.')
        return self.request.META.get('HTTP_REFERER')


@method_decorator(login_required, name='dispatch')
class JoinGroupFormView(CreateView):
    model = EatingGroupMember

    template_name = "group_view.html"
    fields = ['can_drive', 'notes']

    def get_success_url(self):
        messages.success(self.request, 'Group joined!')
        return reverse_lazy('group-view', kwargs={'group': self.kwargs['group']})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.eating_group = EatingGroup.objects.get(pk=self.kwargs['group'])
        return super(JoinGroupFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(JoinGroupFormView, self).get_context_data(**kwargs)
        ctx['group'] = EatingGroup.objects.get(pk=self.kwargs['group'])
        try:
            ctx['mymembership'] = EatingGroupMember.objects.filter(eating_group=self.kwargs['group'], user=self.request.user)[0]
        except (EatingGroupMember.DoesNotExist, IndexError):
            ctx['mymembership'] = None
        return ctx


