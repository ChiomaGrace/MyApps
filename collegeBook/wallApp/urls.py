from django.urls import path
from . import views
from django.conf import settings # I added this to link the lines of code I added in the settings.py (for the upload photo feature)
from django.conf.urls.static import static # I added this to be able to provide an upload photo feature for the user profile pic. This specifically helps serve/show the user uploaded images

urlpatterns = [
    path('', views.regAndLoginPage),
    path('processRegistration', views.processRegistration, name='process-Registration'),
    path('processLogin', views.processLogin),
    path('home', views.loggedInUsersPage, name='home'),
    path('home/ <int:messageId>', views.loggedInUsersPage, name='home'),
    path('processProfilePic', views.processProfilePic),
    path('userDeletesProfilePic', views.userDeletesProfilePic),
    path('processProfileInfo', views.processProfileInfo),
    path('processMessage/<str:userFirstName>/<str:userLastName>/<int:userId>', views.processMessage, name='processMessage'),
    path('processComment/<str:userFirstName>/<str:userLastName>/<int:userId>', views.processComment, name='processComment'),
    path('<str:userFirstName>/<str:userLastName>/<int:userId>', views.specificUsersPage, name='specificUsersPage'),
    path('<str:userFirstName>/<str:userLastName>/<int:userId>/<int:messageId>', views.specificUsersPage, name='specificUsersPage'), #route used when a message is like
    path('like/<int:messageId>', views.userLikes, name='processLike'),
    path('unlike/<int:messageId>', views.userUnlikes),
    path('addFriend/<int:userId>', views.addFriend),
    path('logout', views.logout)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)# I added this to be able to provide an upload photo feature for the user profile pic. This specifically links to the media file that I defined in the settings.py
