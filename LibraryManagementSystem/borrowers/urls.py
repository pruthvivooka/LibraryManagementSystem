from django.conf.urls import url

from . import views
app_name = 'borrowers'
urlpatterns = [
	url(r'^$', views.home, name='home'),
]
