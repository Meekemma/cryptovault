from django.urls import path
from . import views

urlpatterns = [
    path('referrals/', views.create_referral, name='create-referral'),
    path('referrers/<int:user_id>/', views.referrer_stats, name='referrer-info'),
    path('contact/', views.create_contact, name='contact'),
    path('get_currency/', views.get_currency, name='get_currency'),
    path('trending/', views.trending_coin, name='trending'),
    path('intraday/', views.intraday, name='intraday'),

]
