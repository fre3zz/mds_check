from django.urls import path

from mdscheck.views import IndexView, logoutview, RandomMdsCaseView, SearchView, MdsCaseView, aboutview, AnswersView, \
    EmailChangeView, EmailEnterView, continueview, LastAnswersView

app_name = 'mds_check'

urlpatterns = [
    path('about', aboutview, name='about'),
    path('email', EmailEnterView.as_view(), name='email_form'),
    path('email/change', EmailChangeView.as_view(), name='email_change'),
    path('logout/', logoutview, name='logout'),
    path('mdscase/', RandomMdsCaseView.as_view(), name='random_mds_case'),
    path('case_search/', SearchView.as_view(), name='search'),
    path('case_search/<int:case_number>', MdsCaseView.as_view(), name='mds_case'),
    path('', IndexView.as_view(), name='index'),
    path('user/stats', AnswersView.as_view(), name='stats'),
    path('user/stats/last', LastAnswersView.as_view(), name='last_stats'),
    path('continue/', continueview, name='continue'),

]
