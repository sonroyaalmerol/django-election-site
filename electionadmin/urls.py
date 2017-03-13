from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.dashboard, name='dashboard'),
	url(r'^generate/$', views.generate, name='generate'),
	url(r'^voter/delete/(?P<pk>\d+)/$', views.deletevoter, name='deletevoter'),
	url(r'^candidate/add/$', views.addcandidate, name='addcandidate'),
	url(r'^candidate/edit/$', views.editcandidate, name='editcandidate'),
	url(r'^candidate/delete/(?P<pk>\d+)/$', views.deletecandidate, name='deletecandidate'),
	url(r'^election/start/$', views.electionstart, name='electionstart'),
	url(r'^election/stop/$', views.electionstop, name='electionstop'),
	url(r'^election/reset/$', views.electionreset, name='electionreset'),
]
