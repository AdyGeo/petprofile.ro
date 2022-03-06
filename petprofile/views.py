from django.http.response import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from .models import PetProfile, Comment, Notification, Species, Breed, EmailNotificationsAccept, PetProfileExtraImage
from carousel.models import Carousel
from .forms import PetProfileCreateForm, PetProfileUpdateForm
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.mail import EmailMessage
import threading

decorators = [never_cache,]

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=True)


class PetProfileDetailView(DetailView):
    model = PetProfile
    context_object_name = 'pet'
    slug_url_kwarg = "petSlug"
    slug_field = "petSlug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        isOwner = self.request.user == self.object.owner
        limit = 3 if isOwner else 4
        context['extra_photos'] = PetProfileExtraImage.objects.filter(petProfile=self.object.pk).order_by('-pk')[:limit]
        context['petprofile_comments'] = Comment.objects.annotate(main_thread=Coalesce('comment_main_thread', 'pk')).filter(petProfile=self.object.pk,active=True).order_by('main_thread','created')
        context['petprofile_liked'] = False
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        context['query_string'] = query_string
        if self.request.user.is_authenticated:
            liked_profiles = self.object.petLikes.filter(username=self.request.user)
            if liked_profiles:
                context['petprofile_liked'] = True 
        return context

@method_decorator(decorators, name='dispatch')
class PetProfileListView(ListView):
    model = PetProfile
    paginate_by = 12
    context_object_name = 'petprofiles'
    ordering = '-id'

    def get_queryset(self):

        sort_dic = {
            'Cele mai noi':'-id',
            'Data ultimei actualizari':'-PetProfileUpdateDate',
            'Aprecieri descrescator':'-numLikes',
            'Comentarii descrescator':'-numComments'
        }

        qs = super().get_queryset()
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        order = self.request.GET.get('order')
        
        if query is not None:
            query_raw = '|'.join(query.split())
            search_vector = SearchVector('petName', 'petSpecies__species_name', 'petBreed__breed_name',config='ro')
            search_query = SearchQuery(query_raw, search_type='raw')
            
            qs = qs.annotate(search=search_vector).filter(Q(search=search_query) | Q(petName__icontains=query) | Q(petSpecies__species_name__icontains=query) | Q(petBreed__breed_name__icontains=query))

        if category is not None and category.lower() != 'toate':
            qs = qs.filter(petSpecies__species_name__icontains=category)
        
        if order is not None and order in sort_dic:
            if sort_dic[order] == '-numLikes':
                qs = qs.annotate(numLikes=Count('petLikes'))
            elif sort_dic[order] == '-numComments':
                qs = qs.annotate(numComments=Count('comments'))
            qs = qs.order_by(sort_dic[order])

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banners"] = Carousel.objects.filter(active=True).order_by('position')
        context["categories"] = Species.objects.all()
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        context['query_string'] = query_string
        return context

class PetProfileCreateView(LoginRequiredMixin, CreateView):
    model = PetProfile
    form_class = PetProfileCreateForm
    template_name_suffix = '_create'
    
    def get_success_url(self):
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('petprofile-detail',kwargs={'petSlug':self.object.petSlug})+query_string

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return super().form_valid(form)

class PetProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PetProfile
    form_class = PetProfileUpdateForm
    context_object_name = 'pet'
    template_name_suffix = '_update'
    slug_url_kwarg = "petSlug"
    slug_field = "petSlug"

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def form_valid(self, form):
        if form.cleaned_data.get('delete_image'):
            form.instance.petPhoto = None
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('petprofile-detail',kwargs={'petSlug':self.object.petSlug})+query_string

#AJAX
@csrf_exempt
def likePet(request):
    if request.is_ajax and request.method == 'POST':

        if request.user.is_anonymous:
            return JsonResponse({'is_auth':False})

        pk = request.POST.get('pk')
        pet = get_object_or_404(PetProfile, pk=pk)
        if request.user in pet.petLikes.all():
            liked = False
            pet.petLikes.remove(request.user)
        else:
            liked = True
            pet.petLikes.add(request.user)
            # add like - notification_type=1
            if(request.user != pet.owner):
                new_notification = Notification(notification_type=1,to_user=pet.owner,from_user=request.user,petProfile=pet)
                new_notification.save()
                check_email_notif = EmailNotificationsAccept.objects.get_or_create(user=pet.owner)[0]
                if(check_email_notif.email_notif):
                    email = EmailMessage(
                        'Notificare PetProfile | Apreciere noua',
                        f'''Buna,

{request.user.username} a apreciat pet-profilul {pet.petName.title()}:

Acceseaza pagina profilului:
https://petprofile.ro/petprofile/{pet.petSlug}/

Vizualizeaza pet-profilurile utilizatorului {request.user.username}:
https://petprofile.ro/user/{request.user.pk}/petprofiles/


Daca nu mai doresti sa primesti notificari pe e-mail din partea PetProfile, poti dezactiva aceasta optiune accesand sectiunea "notificari" a contului tau:
https://petprofile.ro/petprofile/notifications/
''',
                        'petprofile.contact@gmail.com',
                        [pet.owner.email]
                    )
                    EmailThread(email).start()
        return JsonResponse({'is_auth':True, 'liked':liked, 'likes_count':pet.likesCount})

# AJAX
def load_breeds(request):
    species_id = request.GET.get('species_id')
    breeds = Breed.objects.filter(species=species_id).all()
    return render(request, 'petprofile/breeds_dropdown_list_options.html', {'breeds': breeds})

class PetProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PetProfile
    context_object_name = "pet"
    template_name_suffix = "_delete"
    fileds = ['petName','petSpecies','petBreed','petGender']
    slug_url_kwarg = "petSlug"
    slug_field = "petSlug"
    success_url = reverse_lazy('user-petprofiles') # change this to pet  profiles administration page

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['comment','parent_comment','comment_main_thread']
    def get_success_url(self):
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('petprofile-detail',kwargs={'petSlug':self.kwargs.get('petSlug')})+query_string+'#petprofile-comments'

    def form_valid(self, form):
        pet = get_object_or_404(PetProfile,petSlug=self.kwargs.get('petSlug'))
        form.instance.commentator = self.request.user
        form.instance.petProfile = pet
        form.save()
        # add comment notification - notification_type=2
        if(self.request.user != pet.owner):
            new_notification = Notification(notification_type=2,to_user=pet.owner,from_user=self.request.user,petProfile=pet,comment=form.instance.comment)
            new_notification.save()
            check_email_notif = EmailNotificationsAccept.objects.get_or_create(user=pet.owner)[0]
            if(check_email_notif.email_notif):
                email = EmailMessage(
                    'Notificare PetProfile | Comentariu nou',
                    f'''Buna,
                    
{self.request.user.username} a postat un comentariu pentru {pet.petName.title()}:
Comentariu: "{form.instance.comment}"

Vezi comentariul:
https://petprofile.ro/petprofile/{pet.petSlug}/


Daca nu mai doresti sa primesti notificari pe e-mail din partea PetProfile, poti dezactiva aceasta optiune accesand sectiunea "notificari" a contului tau:
https://petprofile.ro/petprofile/notifications/
''',
                    'petprofile.contact@gmail.com',
                    [pet.owner.email]
                )
                EmailThread(email).start()
        if(form.instance.parent_comment and self.request.user != form.instance.parent_comment.commentator and form.instance.parent_comment.commentator != pet.owner):
            new_notification = Notification(notification_type=3,to_user=form.instance.parent_comment.commentator,from_user=self.request.user,petProfile=pet,comment=form.instance.comment)
            new_notification.save()
            check_email_notif = EmailNotificationsAccept.objects.get_or_create(user=form.instance.parent_comment.commentator)[0]
            if(check_email_notif.email_notif):
                email = EmailMessage(
                    'Notificare PetProfile | Raspuns comentariu',
                    f'''Buna,
                    
{self.request.user.username} a raspuns la un comentariu postat de tine la pet-profilul {pet.petName.title()}:
Comentariul tau: "{form.instance.parent_comment.comment}""
Raspuns primit: "{form.instance.comment}"

Vezi comentariul:
https://petprofile.ro/petprofile/{pet.petSlug}/


Daca nu mai doresti sa primesti notificari pe e-mail din partea PetProfile, poti dezactiva aceasta optiune accesand sectiunea "notificari" a contului tau:
https://petprofile.ro/petprofile/notifications/
''',
                    'petprofile.contact@gmail.com',
                    [form.instance.parent_comment.commentator.email]
                )
                EmailThread(email).start()

        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        return redirect('homepage')


class CommentInactiveView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    context_object_name = 'comment'
    def test_func(self):
        obj = self.get_object()
        return obj.commentator == self.request.user or obj.petProfile.owner == self.request.user

    def get_success_url(self):
        comm = self.get_object()
        pet = comm.petProfile.petSlug
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('petprofile-detail',kwargs={'petSlug':pet})+query_string+'#petprofile-comments'
    
    def get(self, request, *args, **kwargs):
        return redirect('homepage')


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    context_object_name = 'comment'
    fields = ['comment']
    def test_func(self):
        obj = self.get_object()
        return obj.commentator == self.request.user and obj.active

    def get_success_url(self):
        comm = self.get_object()
        pet = comm.petProfile.petSlug
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('petprofile-detail',kwargs={'petSlug':pet})+query_string+'#petprofile-comments'
    
    def get(self, request, *args, **kwargs):
        return redirect('homepage')


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    context_object_name = 'notifications'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(to_user=self.request.user)

        if qs:
            new_notifs = qs.exclude(user_has_seen=True)
            for notif in new_notifs:
                notif.user_has_seen = True
                notif.save()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_email_notif_acc = EmailNotificationsAccept.objects.get_or_create(user=self.request.user)[0]
        context['email_notif'] = user_email_notif_acc.email_notif
        return context
    
class PetExtraPhotosListView(ListView):
    model = PetProfileExtraImage
    context_object_name = 'extra_photos'

    def get_queryset(self):
        pet = get_object_or_404(PetProfile,petSlug=self.kwargs.get('petSlug'))
        qs = PetProfileExtraImage.objects.filter(petProfile=pet).order_by('-pk')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = get_object_or_404(PetProfile,petSlug=self.kwargs.get('petSlug'))
        context['petName'] = pet.petName
        context['petSlug'] = pet.petSlug
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        context['query_string'] = query_string

        return context

class PetExtraPhotosCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = PetProfileExtraImage
    fields = ['petExtraImg']

    def get_success_url(self):
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('petprofile-detail',kwargs={'petSlug':self.kwargs.get('petSlug')})+query_string

    def test_func(self):
        pet = get_object_or_404(PetProfile,petSlug=self.kwargs.get('petSlug'))
        return pet.owner == self.request.user
    
    def form_valid(self, form):
        pet = get_object_or_404(PetProfile,petSlug=self.kwargs.get('petSlug'))
        form.instance.petProfile = pet
        form.save()
        pet.save()
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        return redirect('homepage')


class ExtraImgDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PetProfileExtraImage
    context_object_name = 'extra_img'
    def test_func(self):
        obj = self.get_object()
        return obj.petProfile.owner == self.request.user

    def get_success_url(self):
        img = self.get_object()
        petSlug = img.petProfile.petSlug
        query_string = f'?{self.request.GET.urlencode()}' if self.request.GET else ''
        return reverse_lazy('pet-extra-photos',kwargs={'petSlug':petSlug})+query_string
    
    def get(self, request, *args, **kwargs):
        return redirect('homepage')