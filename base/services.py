from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
from typing import Dict, Any
import requests
from django.contrib.auth import get_user_model

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# URLs for Google OAuth2 token exchange and user info
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'




def google_get_access_and_refresh_tokens(code: str, redirect_uri: str) -> Dict[str, str]:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'access_type': 'offline',
        'prompt': 'consent'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    logger.debug(f'Response from token exchange: {response.json()}')

    if not response.ok:
        logger.error(f'Error obtaining tokens: {response.content}')
        raise ValidationError('Could not get tokens from Google.')
    
    tokens = response.json()
    return tokens

def google_get_user_info(access_token: str) -> Dict[str, Any]:
    response = requests.get(GOOGLE_USER_INFO_URL, params={'access_token': access_token})
    logger.debug(f'Response from user info: {response.json()}')

    if not response.ok:
        logger.error(f'Error obtaining user info: {response.content}')
        raise ValidationError('Could not get user info from Google.')
    
    return response.json()

def get_user_data(validated_data: Dict[str, str]) -> Dict[str, str]:
    domain = settings.BASE_API_URL
    redirect_uri = f'{domain}/google-login/'
    code = validated_data.get('code')
    error = validated_data.get('error')

    if error or not code:
        logger.error(f'Error or no code provided: {error}')
        raise ValidationError('Error or no code provided.')

    tokens = google_get_access_and_refresh_tokens(code=code, redirect_uri=redirect_uri)
    logger.debug(f'Tokens: {tokens}')
    
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token')

    user_data = google_get_user_info(access_token=access_token)
    logger.debug(f'User data from Google: {user_data}')

    user, created = User.objects.get_or_create(
        email=user_data['email'],
        defaults={
            'first_name': user_data.get('given_name'),
            'last_name': user_data.get('family_name'),
        }
    )
    if created:
        user.auth_provider = 'google'
        user.is_verified = True
        user.save()

    profile_data = {
        'id': user.id, 
        'email': user_data['email'],
        'first_name': user_data.get('given_name'),
        'last_name': user_data.get('family_name'),
    }

    return profile_data
