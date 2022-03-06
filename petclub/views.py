from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from .forms import UserDeleteForm
from django.contrib import messages
from django.contrib.auth import logout
from petprofile.models import PetProfile, EmailNotificationsAccept
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(user_signed_up)
def register_user_to_notif(sender, user, **kwargs):
    new_notif_acc = EmailNotificationsAccept(user=user)
    new_notif_acc.save()


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /petprofile/create/",
        "Disallow: /petprofile/update/",
        "Disallow: /petprofile/delete/",
        "Disallow: /petprofile/likepet/",
        "Disallow: /petprofile/comment/",
        "Disallow: /petprofile/notifications/",
        "Disallow: /petprofile/ajax/",
	"Disallow: /petprofile/add-photo/",
	"Disallow: /petprofile/delete-photo/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    fields = ['username','first_name','last_name','email']
    context_object_name = 'userprofile'
    template_name = 'account/userprofile_detail.html'

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_email_notif_acc = EmailNotificationsAccept.objects.get_or_create(user=self.request.user)[0]
        context['email_notif'] = user_email_notif_acc.email_notif
        return context

class UserPetProfilesView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'userprofile'
    template_name = 'account/userprofile_petprofiles.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ownPetProfiles'] = self.request.user.petprofile_set.all()
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username','first_name','last_name']
    context_object_name = 'userprofile'
    template_name = 'account/userprofile_update.html'
    success_url = reverse_lazy('userprofile')

    def get_object(self):
        return self.request.user


class UserProfileDeleteView(LoginRequiredMixin, View):
    """
    Deletes the currently signed-in user and all associated data.
    """
    def get(self, request, *args, **kwargs):
        form = UserDeleteForm()
        return render(request, 'account/userprofile_delete.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserDeleteForm(request.POST)
        # Form will be valid if checkbox is checked.
        if form.is_valid():
            user = request.user
            # Logout before we delete. This will make request.user
            # unavailable (or actually, it points to AnonymousUser).
            logout(request)
            # Delete user (and any associated ForeignKeys, according to
            # on_delete parameters).
            user.delete()
            messages.success(request, 'Contul tau a fost sters')
            return redirect(reverse('homepage'))
        return render(request, 'account/userprofile_delete.html', {'form': form})

class SomeUserPetProfilesView(DetailView):
    model = User
    context_object_name = 'someuser'
    template_name='account/someuser_petprofiles.html'

    def get_context_data(self, **kwargs):
        someuser = self.get_object()
        context = super().get_context_data(**kwargs) if someuser.pk != 1 else {}
        context['someuser_petprofiles'] = PetProfile.objects.filter(owner=someuser)
        return context


class UserEmailNotifView(LoginRequiredMixin, UpdateView):
    model = EmailNotificationsAccept
    fields = ['email_notif']
    context_object_name = 'user_email_notif'

    def get_object(self):
        user_notif_acc = EmailNotificationsAccept.objects.get_or_create(user=self.request.user)[0]
        return user_notif_acc
    
    def get_success_url(self, **kwargs): 
        next = self.request.GET.get('next', '/')
        return reverse_lazy(next)
    
    def get(self, request, *args, **kwargs):
        return redirect('homepage')


class AboutUsView(TemplateView):
    template_name = 'about.html'

class InfoCookiesView(TemplateView):
    template_name = 'info_cookies.html'

class InfoConfidentialitateView(TemplateView):
    template_name = 'info_confidentialitate.html'
