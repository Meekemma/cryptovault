from django.urls import path
from . import views

urlpatterns = [
    # path('referrers/<int:user_id>/', views.referrer_stats, name='referrer-info'),
    path('referral-details/', views.get_referral_details, name='referral-details'),
    path('contact/', views.create_contact, name='contact'),
    path('get_currency/', views.get_currency, name='get_currency'),
    path('trending/', views.trending_coin, name='trending'),
    path('intraday/', views.intraday, name='intraday'),

]
