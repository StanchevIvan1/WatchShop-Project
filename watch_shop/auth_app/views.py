from django import forms
from django.contrib.auth import forms as auth_forms, views as auth_views, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic as views

from watch_shop.auth_app.forms import SignUpForm
from watch_shop.auth_app.models import Profile
from watch_shop.auth_app.tasks import send_email_to_new_users
from watch_shop.web.models import ShoppingCart, ShoppingProduct

UserModel = get_user_model()


class SignUpView(views.CreateView):
    template_name = 'auth/sign-up.html'
    form_class = SignUpForm

    success_url = reverse_lazy('index')

    def form_valid(self, form):
        result = super().form_valid(form)

        login(self.request, self.object)

        send_email_to_new_users(self.request.user.email)
        return result


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SignInView(auth_views.LoginView):
    template_name = 'auth/sign-in.html'
    success_url = reverse_lazy('index')


class SignOutView(auth_views.LogoutView):
    template_name = 'auth/sign-out.html'


class UserDetailsView(views.DetailView):
    template_name = 'account/account_details.html'
    model = UserModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_owner'] = self.request.user == self.object
        context['purchases'] = ShoppingCart.objects.filter(user_id=self.request.user.pk).get().product.filter() \
            if ShoppingCart.objects.filter(user_id=self.request.user.pk) else None
        context['count'] = ShoppingProduct.objects.filter(shoppingcart__user_id=self.request.user.pk).count()
        return context


class UserEditView(LoginRequiredMixin, views.UpdateView, PermissionRequiredMixin):
    template_name = 'account/account_edit.html'
    model = Profile
    fields = ('first_name', 'last_name', 'age', 'photo')

    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        if not self.request.user.pk == self.kwargs['pk']:
            return redirect('index')
        return super().get(self.request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('user details', kwargs={
            'pk': self.request.user.pk,
        })


class UserDeleteView(LoginRequiredMixin, views.DeleteView):
    template_name = 'account/account_delete.html'
    model = UserModel
    success_url = reverse_lazy('index')

    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        if not self.request.user.pk == self.kwargs['pk']:
            return redirect('index')
        return super().get(self.request, *args, **kwargs)
