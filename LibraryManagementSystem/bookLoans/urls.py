from django.conf.urls import url

from . import views
app_name = 'bookLoans'
urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^checkOut$', views.checkOut, name='checkOut'),
	url(r'^checkIn$', views.checkIn, name='checkIn'),
	url(r'^bookCheckIn$', views.bookCheckIn, name='bookCheckIn'),
	url(r'^fines$', views.fines, name='fines'),
	url(r'^finesUpdate$', views.finesUpdate, name='finesUpdate'),
	url(r'^payFine$', views.payFine, name='payFine'),
]