from django.urls import path

from mdscheck.views import IndexView, EmailEnterView, logoutview, MdsCaseView


app_name = 'mds_check'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('email', EmailEnterView.as_view(), name='email_form'),
    path('logout', logoutview, name='logout'),
    path('mdscase', MdsCaseView.as_view(), name='mds_case')
]
