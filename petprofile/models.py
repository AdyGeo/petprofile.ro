from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, RESTRICT
from django.utils.text import slugify
from django.urls import reverse
import os

def _img_dir_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    #og_filename = os.path.splitext(filename)[0]
    new_filename = f'petprofile-photo/{instance.petSlug}{extension}%'
    return new_filename

def _extra_img_dir_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    #og_filename = os.path.splitext(filename)[0]
    new_filename = f'petprofile-extra-images/{instance.petProfile.petSlug}{extension}%'
    return new_filename

default_petPhoto = 'petprofile-photo/avatar.png'

PETGENDER_CHOICES = (
    ("M","Mascul"),
    ("F","Femela"),
    ("N","Nespecificat")
)


class Species(models.Model):
    species_name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'species'
        ordering = ['species_name']

    def __str__(self):
        return self.species_name

class Breed(models.Model):
    species = models.ForeignKey("Species", on_delete=models.RESTRICT)
    breed_name = models.CharField(max_length=35)
    
    class Meta:
        ordering = ['breed_name']

    def __str__(self):
        return self.breed_name

class PetProfile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    petName = models.CharField("Nume",max_length=30, null=False, blank=False)
    petSlug = models.SlugField(max_length=120, unique=True)
    petGender = models.CharField("Gen",max_length=10, null=False, blank=False, choices=PETGENDER_CHOICES)
    petDescription = models.TextField("Scurta descriere",max_length=2000, null=False, blank=False)
    petPhoto = models.ImageField("Foto",upload_to=_img_dir_path,blank=True, max_length=200, default=default_petPhoto)
    petProfileCreationDate = models.DateField("Data creare profil", auto_now_add=True)
    PetProfileUpdateDate = models.DateTimeField(auto_now=True)
    petSpecies = models.ForeignKey("Species",on_delete=RESTRICT, verbose_name='Categorie')
    petBreed = models.ForeignKey("Breed", on_delete=RESTRICT, verbose_name='Subspecie/Rasa')
    petLikes = models.ManyToManyField(User, verbose_name="Likes", related_name="profileLikes", blank=True)

    def __str__(self):
        return self.petSlug

    def get_absolute_url(self):
        return reverse("petprofile-detail", kwargs={"petSlug": self.petSlug})
    
    @property
    def likesCount(self):
        return self.petLikes.count()
    
    @property
    def commentsCount(self):
        return self.comments.filter(active=True).count()

    def _generate_unique_slug(self):
        slug_participants = [slugify(self.petName),slugify(self.petSpecies),slugify(self.petBreed)]
        slug = "-".join(slug_participants)
        num = None
        while PetProfile.objects.filter(petSlug=(slug + '-' + str(num) if num else slug)).exclude(pk=self.pk).exists():
            num = int(num or 1) + 1
        unique_slug = slug + '-' + str(num) if num else slug
        return unique_slug
    
    def save(self, *args, **kwargs):
        if not self.petPhoto:
            self.petPhoto = default_petPhoto
        self.petSlug = self._generate_unique_slug()
        super().save(*args, **kwargs)

class Comment(models.Model):
    petProfile = models.ForeignKey(PetProfile,on_delete=models.CASCADE, related_name='comments')
    commentator = models.ForeignKey(User,on_delete=CASCADE, related_name='commentator')
    comment = models.TextField(max_length=1000, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    comment_main_thread = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('created',)
    def __str__(self):
        return self.comment

class Notification(models.Model):
    #1 = Like, 2 = Comment, 3 = Comment reply
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE)
    petProfile = models.ForeignKey(PetProfile, related_name='+', on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user_has_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return 'like notification' if self.notification_type == 1 else 'comment notification'


class EmailNotificationsAccept(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_notif = models.BooleanField(verbose_name=("email_notifications"), default=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Email Notifications Acceptance'

class PetProfileExtraImage(models.Model):
    petProfile = models.ForeignKey(PetProfile, related_name="pet_imgs", on_delete=models.CASCADE)
    petExtraImg = models.ImageField("PetExtraImg",upload_to=_extra_img_dir_path, max_length=200, blank=False, null=False)

    def __str__(self):
        return self.petProfile.petSlug