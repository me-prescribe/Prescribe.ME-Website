from django.contrib import admin
from django.urls import path
from miniapp.views import usignup,ulogin,ulogout,uresetpassword,feedback,home,prescribe,profile,prescription_page,patient,send_prescription
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home,name="home"),
    path("usignup/",usignup,name="usignup"),
    path("ulogin/",ulogin,name="ulogin"),
    path("ulogout/",ulogout,name="ulogout"),
    path("uresetpassword/",uresetpassword,name="uresetpassword"),
    path("feedback/",feedback,name="feedback"),
    path("prescribe/",prescribe,name="prescribe"),
    path("patient/",patient,name="patient"),
    path("profile/",profile,name="profile"),
    path("presription/",prescription_page,name="prescription_page"),
    path("send_prescription/",send_prescription,name="send_prescription"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
