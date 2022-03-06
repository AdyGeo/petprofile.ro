from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from django.db.models import Max

from petprofile.models import PetProfile, Comment


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['homepage', 'about', 'info-cookies', 'info-confidentialitate']
    def priority(self, item):
        return {'homepage': 0.8, 'about': 0.5, 'info-cookies': 0.5,'info-confidentialitate': 0.5}[item]
    def changefreq(self, item):
        return {'homepage': 'weekly', 'about': 'yearly', 'info-cookies': 'yearly','info-confidentialitate': 'yearly'}[item]
    def location(self, item):
        return reverse(item)

class PetProfileViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    def items(self):
        pets = PetProfile.objects.all()
        for pet in pets:
            pet_comments = Comment.objects.filter(petProfile=pet.pk).aggregate(Max('updated'))
            pet.upd_date = max(pet.PetProfileUpdateDate, pet_comments['updated__max'] if pet_comments['updated__max'] else pet.PetProfileUpdateDate)
        return pets
    def lastmod(seld, obj):
        return obj.upd_date

class ExtraImgViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    def items(self):
        return PetProfile.objects.filter(pet_imgs__petExtraImg__isnull=False).distinct()
    def lastmod(seld, obj):
        return obj.PetProfileUpdateDate
    def location(self, item):
        return reverse('pet-extra-photos',kwargs={'petSlug': item.petSlug})