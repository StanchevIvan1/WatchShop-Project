from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic as views
from rest_framework import generics as api_views
from rest_framework import serializers

from watch_shop.auth_app.models import AppUser
from watch_shop.auth_app.tasks import send_email_when_checkout_invoked
from watch_shop.web.forms import ProductEditForm, ContactForm
from watch_shop.web.models import Product, ShoppingCart, ShoppingProduct

UserModel = get_user_model()


class IndexView(views.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = reversed(Product.objects.filter().order_by('-id')[:3][::-1])
        context['count'] = ShoppingProduct.objects.filter(shoppingcart__user_id=self.request.user.pk).count()
        return context


class AboutView(views.TemplateView):
    template_name = 'about.html'


class ContactView(views.TemplateView):
    template_name = 'contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm
        return context


class ProductsView(LoginRequiredMixin, views.ListView):
    template_name = 'products.html'
    model = Product
    context_object_name = 'products_list'
    paginate_by = 9
    ordering = ['id']

    def purchase(self, pk, product_id):
        cart, __ = ShoppingCart.objects.get_or_create(user_id=pk)

        instance, created = ShoppingProduct.objects.get_or_create(product_id=product_id, shoppingcart_id=cart.user_id)
        if not created:
            instance.quantity = instance.quantity + 1
            instance.save()
            return redirect("products")
        else:
            instance.save()
            return redirect("products")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.groups.filter(name='staff').exists()
        context['is_admin'] = self.request.user.groups.filter(name='admin').exists()
        context['count'] = ShoppingProduct.objects.filter(shoppingcart__user_id=self.request.user.pk).count()
        return context


class ShoppingCartView(views.ListView):
    template_name = 'shoppingcart.html'
    model = ShoppingCart
    context_object_name = 'ShoppingCart_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        list_quantities = []
        for i in ShoppingProduct.objects.filter(shoppingcart_id=self.request.user.pk):
            list_quantities.append(i)

        context['products'] = list_quantities
        context['total'] = sum(i.product.price * i.quantity for i in list_quantities)
        context['items'] = ShoppingCart.objects.filter(user_id=self.request.user.pk).get() \
            .product.filter(shoppingproduct__shoppingcart_id=self.request.user.pk) \
            if ShoppingCart.objects.filter(user_id=self.request.user.pk) else None
        context['count'] = ShoppingProduct.objects.filter(shoppingcart__user_id=self.request.user.pk).count()
        return context

    def remove_item_from_cart(self, pk, product_id):
        try:
            cart = ShoppingCart.objects.get(user_id=pk)
            entry_to_delete = ShoppingProduct.objects.get(shoppingcart_id=cart.user_id, product_id=product_id)
            entry_to_delete.delete()
        except ShoppingProduct.DoesNotExist:
            return redirect('cart')
        return redirect('cart')

    def clear_cart(self, pk):
        cart = ShoppingCart.objects.get(user_id=pk)
        entry_to_delete = ShoppingProduct.objects.filter(shoppingcart_id=cart.user_id)
        for product in entry_to_delete:
            try:
                entry_to_delete.delete()
            except ShoppingProduct.DoesNotExist:
                continue
        return redirect('cart')

    def checkout(self, pk):
        cart = ShoppingCart.objects.get(user_id=pk)
        entry_to_delete = ShoppingProduct.objects.filter(shoppingcart_id=cart.user_id)
        context = {
            'cart_id': cart.user_id,
            'total_sum': 0,
        }
        for product in entry_to_delete:
            try:
                context['total_sum'] += product.product.price * product.quantity
                entry_to_delete.delete()
            except ShoppingProduct.DoesNotExist:
                continue

        send_email_when_checkout_invoked(email=AppUser.object.get(pk=pk).email, order=True)
        return render(request=self, template_name='checkout_page.html', context=context)

    def add_item(self, pk, product_id):
        cart = ShoppingCart.objects.get(user_id=pk)

        instance = ShoppingProduct.objects.get(product_id=product_id, shoppingcart_id=cart.user_id)
        instance.quantity = instance.quantity + 1
        instance.save()
        return redirect("cart")

    def subtract_item(self, pk, product_id):
        cart = ShoppingCart.objects.get(user_id=pk)

        instance = ShoppingProduct.objects.get(product_id=product_id, shoppingcart_id=cart.user_id)
        try:
            instance.quantity = instance.quantity - 1
            instance.save()
            return redirect("cart")
        except IntegrityError:
            return redirect('remove product', pk=pk, product_id=product_id)


class ProductEditView(LoginRequiredMixin, views.UpdateView, PermissionRequiredMixin):
    template_name = 'product_edit.html'
    model = Product
    form_class = ProductEditForm

    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        if not self.request.user.groups.filter(name__in=['staff', 'admin']).exists():
            return redirect('index')
        return super().get(self.request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductsApiView(api_views.ListAPIView):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
