import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from management.serializers import ReferralSerializer,ReferrerStatsSerializer,RefereeBaseSerializer,ContactSerializer
from base.models import UserProfile
from management.models import Referral
from django.contrib.auth import get_user_model
User = get_user_model()




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_details(request):
    """
    Retrieves referral details for the authenticated user.
    """
    try:
        user_profile = request.user.userprofile
        referrals = Referral.objects.filter(referrer=user_profile)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    if not referrals.exists():
        return Response({"message": "No referrals yet."}, status=status.HTTP_200_OK)

    serializer = ReferralSerializer(referrals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





# @api_view(['GET'])
# def referrer_stats(request, user_id):
#     try:
#         # Retrieve the referrer based on user_id
#         referrer = User.objects.get(id=user_id)
        
#         # Retrieve the referrer profile
#         referrer_profile = referrer.userprofile
        
#         # Calculate total bonus and total referees count
#         total_bonus = Referral.get_accumulated_bonus(referrer_profile)
#         total_referees = Referral.get_referee_count(referrer_profile)
        
#         # Get referees
#         referees = Referral.get_referees(referrer_profile)
        
#         # Serialize data
#         referrer_stats_serializer = ReferrerStatsSerializer({
#             'total_bonus': total_bonus,
#             'total_referees': total_referees
#         })
#         referee_serializer = RefereeBaseSerializer(referees, many=True)
        
#         # Prepare response data
#         data = {
#             'referrer_stats': referrer_stats_serializer.data,
#             'referees': referee_serializer.data
#         }
        
#         # Return serialized data as JSON response
#         return Response(data, status=status.HTTP_200_OK)
    
#     except User.DoesNotExist:
#         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)






@api_view(['POST'])
def create_contact(request):
    if request.method == 'POST':
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


	#CG-JeHDGtmLXazohfDQcJNLpjQV


@api_view(['GET'])
def get_currency(request):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    
    # Add query parameters
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false"
    }

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-JeHDGtmLXazohfDQcJNLpjQV"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        return Response(data, status=status.HTTP_200_OK)
    except requests.exceptions.HTTPError as errh:
        return Response({"error": str(errh)}, status=response.status_code)
    except requests.exceptions.ConnectionError as errc:
        return Response({"error": "Error Connecting: " + str(errc)}, status=status.HTTP_502_BAD_GATEWAY)
    except requests.exceptions.Timeout as errt:
        return Response({"error": "Timeout Error: " + str(errt)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as err:
        return Response({"error": "Something went wrong: " + str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def trending_coin(request):
    url = "https://api.coingecko.com/api/v3/search/trending"
    
    params = {
        'page': 1,
        'per_page': 2,
        "sparkline": "false"
        
       
    }

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-JeHDGtmLXazohfDQcJNLpjQV"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        return Response(data, status=status.HTTP_200_OK)
    except requests.exceptions.HTTPError as errh:
        return Response({"error": str(errh)}, status=response.status_code)
    except requests.exceptions.ConnectionError as errc:
        return Response({"error": "Error Connecting: " + str(errc)}, status=status.HTTP_502_BAD_GATEWAY)
    except requests.exceptions.Timeout as errt:
        return Response({"error": "Timeout Error: " + str(errt)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as err:
        return Response({"error": "Something went wrong: " + str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







@api_view(['GET'])
def intraday(request):
    symbol = request.query_params.get('symbol', 'IBM')  # Default to IBM if not provided
    interval = request.query_params.get('interval', '5min')  # Default to 5min if not provided
    
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey=7UPQM1X1OZ7BNJUE'
    
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        # Extract the time series data
        time_series = data.get("Time Series (5min)", {})

        # Get the first 10 entries
        first_10_entries = dict(list(time_series.items())[:10])

        # Create a new response with only the relevant data
        response_data = {
            "Meta Data": data.get("Meta Data"),
            "Time Series (5min)": first_10_entries
        }

        return Response(response_data)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=400)




