"""petclub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from petprofile.views import PetProfileListView
from .views import robots_txt, UserEmailNotifView, SomeUserPetProfilesView, UserPetProfilesView, UserProfileDetailView, UserProfileUpdateView, UserProfileDeleteView, AboutUsView, InfoCookiesView, InfoConfidentialitateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, PetProfileViewSitemap , ExtraImgViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'petprofiles': PetProfileViewSitemap,
    'extraimages': ExtraImgViewSitemap
}

urlpatterns = [
    path('',PetProfileListView.as_view(),name='homepage'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt',robots_txt),
    path('petprofile/',include('petprofile.urls')),
    path('admin/', admin.site.urls),
    path('accounts/profile/', UserProfileDetailView.as_view(), name='userprofile'),
    path('accounts/petprofiles/', UserPetProfilesView.as_view(), name='user-petprofiles'),
    path('accounts/profile/update/', UserProfileUpdateView.as_view(), name='userprofile-update'),
    path('accounts/profile/delete/', UserProfileDeleteView.as_view(), name='userprofile-delete'),
    path('accounts/email-notifs-acc/<int:pk>/', UserEmailNotifView.as_view(), name='email-notif-acc'),
    path('accounts/', include('allauth.urls')),
    path('user/<int:pk>/petprofiles/', SomeUserPetProfilesView.as_view(), name='someuser-petprofiles'),
    path('about/', AboutUsView.as_view(), name='about'),
    path('info-cookies/', InfoCookiesView.as_view(), name='info-cookies'),
    path('info-confidentialitate/', InfoConfidentialitateView.as_view(), name='info-confidentialitate')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)