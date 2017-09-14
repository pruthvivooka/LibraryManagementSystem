from django.conf.urls import url

from . import views
app_name = 'bookSearch'
urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^search$', views.search, name='search'),
]
