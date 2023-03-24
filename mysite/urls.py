from django.contrib import admin
from django.urls import path, include
from StudyBuddy.views import home, Profile, Friends, UserSearchResults, CreateThread, ListThreads, ThreadView, CreateMessage

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('classes/', include('StudyBuddy.urls'), name='classes'),
    path('friends/', Friends.as_view(), name='friends'),
    path('search-users/', UserSearchResults.as_view(), name='search-users'),
    path('profile/', Profile.as_view(), name='profile'),
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),
]
