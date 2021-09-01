from django.urls import path

from mdscheck.views import IndexView, EmailEnterView, logoutview, RandomMdsCaseView, SearchView, MdsCaseView, aboutview, AnswersView

app_name = 'mds_check'





urlpatterns = [
    path('about', aboutview, name='about'),
    path('email', EmailEnterView.as_view(), name='email_form'),
    path('logout/', logoutview, name='logout'),
    path('mdscase/', RandomMdsCaseView.as_view(), name='random_mds_case'),
    path('case_search/', SearchView.as_view(), name='search'),
    path('case_search/<int:case_number>', MdsCaseView.as_view(), name='mds_case'),
    path('', IndexView.as_view(), name='index'),
    path('user/stats', AnswersView.as_view(), name='stats')
]
