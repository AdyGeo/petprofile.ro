from django.contrib import admin
from . models import Carousel
# Register your models here.


class CarouselAdmin(admin.ModelAdmin):
    list_display = ('title','link','banner_img','active','position')

admin.site.register(Carousel,CarouselAdmin)
