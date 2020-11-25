from django.urls import path
from . import views
from django.conf import settings # I added this to link the lines of code I added in the settings.py (for the upload photo feature)
from django.conf.urls.static import static # I added this to be able to provide an upload photo feature for the user profile pic
from django.conf.urls import url, include #trying this ??

urlpatterns = [
    path('', views.loginPage),
    path('processRegistration', views.processRegistration, name='process-Registration'),
    path('processLogin', views.processLogin),
    path('wall', views.loggedInUsersPage),
    path('processProfilePic', views.loggedInUsersPage),
    path('processMessage', views.processMessage),
    path('processComments', views.processComments),
    path('like/<messageId>', views.userLikes),
    path('unlike/<messageId>', views.userUnlikes),
    path('user/<userId>', views.specificUserPage),
    path('logout', views.logout)
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT) # I added this to be able to provide an upload photo feature for the user profile pic
# if settings.DEBUG: # new
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)