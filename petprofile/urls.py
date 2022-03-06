from django.urls import path
from petprofile.views import (ExtraImgDeleteView, PetExtraPhotosCreateView, PetExtraPhotosListView, NotificationListView, CommentEditView, CommentInactiveView, CommentCreateView, PetProfileDetailView,PetProfileCreateView,PetProfileUpdateView, PetProfileDeleteView, likePet, load_breeds)

urlpatterns = [
    path('create/', PetProfileCreateView.as_view(), name='petprofile-create'),
    path('update/<slug:petSlug>/', PetProfileUpdateView.as_view(), name='petprofile-update'),
    path('delete/<slug:petSlug>/', PetProfileDeleteView.as_view(), name='petprofile-delete'),
    path('likepet/', likePet, name='likepet'),
    path('comment/create/<slug:petSlug>/', CommentCreateView.as_view(), name='pet-comment-create'),
    path('comment/delete/<int:pk>/', CommentInactiveView.as_view(), name='pet-comment-delete'),
    path('comment/edit/<int:pk>/',CommentEditView.as_view(), name='pet-comment-edit'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('ajax/load-breeds/', load_breeds, name='ajax-load-breeds'),
    path('photo-album/<slug:petSlug>/',PetExtraPhotosListView.as_view(), name='pet-extra-photos'),
    path('add-photo/<slug:petSlug>/',PetExtraPhotosCreateView.as_view(), name='add-extra-photo'),
    path('delete-photo/<int:pk>/',ExtraImgDeleteView.as_view(), name='delete-extra-photo'),
    path('<slug:petSlug>/', PetProfileDetailView.as_view(), name='petprofile-detail')
]