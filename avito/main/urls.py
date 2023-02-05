from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [
    path('accounts/logout/', AvitoLogoutView.as_view(), name='logout'),
    path('accounts/profile/change/', ChangeUserInfoVIew.as_view(),
                                     name='profile_change'),
    path('accounts/password/change/', AvitoPasswordChangeView.as_view(),
                                      name='password_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/login/', AvitoLoginView.as_view(), name='login'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]
