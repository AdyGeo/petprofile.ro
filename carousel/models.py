from django.db import models

# Create your models here.
class Carousel(models.Model):
    title = models.CharField(max_length=50)
    link = models.URLField()
    banner_img = models.ImageField("Foto",upload_to='banners', null=False, blank=False)
    active = models.BooleanField()
    position = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.link

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'