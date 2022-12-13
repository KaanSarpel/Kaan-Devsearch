from django.contrib import admin
from django.urls import path, include

from django.conf import settings #We want to have access to settings file.
from django.conf.urls.static import static #This will help us to create URL for our static files. Now set urlpatterns.

from django.contrib.auth import views as auth_views #Django docsdan aldık password reset için kullanıcaz.

from users.forms import UserPasswordResetForm , UserSetPasswordForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')),
    path('', include('users.urls')),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="reset_password.html",form_class=UserPasswordResetForm), #User submits email for reset
         name="reset_password"),

    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="reset_password_sent.html"), #Email sent message
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset.html",form_class=UserSetPasswordForm), #Email with link and reset instructions
         name="password_reset_confirm"),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="reset_password_complete.html"),  #Password successfully reset message
         name="password_reset_complete"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #Go to settings grab the Media Url and connect it to Media Root.Now we should style this.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# 1 - User submits email for reset              //PasswordResetView.as_view()           //name="reset_password"
# 2 - Email sent message                        //PasswordResetDoneView.as_view()        //name="passsword_reset_done"
# 3 - Email with link and reset instructions    //PasswordResetConfirmView()            //name="password_reset_confirm"
# 4 - Password successfully reset message       //PasswordResetCompleteView.as_view()   //name="password_reset_complete"
