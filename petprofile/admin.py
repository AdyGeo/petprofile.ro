from django.contrib import admin
from . models import Notification, PetProfile, Species, Breed, Comment, EmailNotificationsAccept, PetProfileExtraImage

# Register your models here.

class PetProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id','petSlug')
    list_display  = ['petName', 'petSpecies', 'petBreed', 'petSlug']

class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('created','updated')
    list_display  = ['comment', 'active', 'commentator', 'petProfile']

class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ['__str__','to_user', 'from_user', 'petProfile', 'created', 'notification_type']

class EmailNotificationsAcceptAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'email_notif']


class PetProfileExtraImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'petExtraImg']
    search_fields =['petExtraImg']


admin.site.register(PetProfile,PetProfileAdmin)
admin.site.register(Species)
admin.site.register(Breed)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(EmailNotificationsAccept, EmailNotificationsAcceptAdmin)
admin.site.register(PetProfileExtraImage,PetProfileExtraImageAdmin)

