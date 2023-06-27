from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_ToVote, name='_loging_'),
    path('atl-eVoting/login', views.login_ToVote, name='_loging_'),
    path('dashboard/', views.dashboard, name='admin'),
    path('logout/', views.log_out_user, name='logout'),
    path('contact/', views.contactUS, name='contactUs'),
    path('voters/', views.view_voters, name='voters'),
    path('atl-eVoting/results', views.view_vote_Results, name='results'),
    path('portfolio/<int:portfolio>', views.view_portfolio, name='portfolio'),
    path('atl-eVoting/vote', views.viewVotePage, name='Voting'),
    path('submit-votes/<int:candidate_id>', views.submitVotes, name='submit_votes'),
    path('send-Vsms/', views.send_credentials, name='send-sms2'),
]


if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

