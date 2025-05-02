from rest_framework import serializers
from .models import Referral,Contact
from base.models import UserProfile





class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= UserProfile
        fields = ['first_name', 'last_name', 'email']
        read_only_fields = ['first_name', 'last_name', 'email', ]



class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['code']

    def create(self, validated_data):
        referral_code = validated_data.get('code')

        # Retrieve the referrer profile associated with the referral code
        try:
            referrer_profile = UserProfile.objects.get(referral_code=referral_code)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid referral code")

        # Retrieve the referee profile from the authenticated user
        user_profile = self.context['request'].user.userprofile

        # Create the Referral instance
        referral = Referral.objects.create(
            referee=user_profile,
            referrer=referrer_profile,
            code=referral_code,
            bonus=50.00  
        )

        return referral



class ReferrerStatsSerializer(serializers.Serializer):
    total_bonus = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_referees = serializers.IntegerField(read_only=True)


class RefereeBaseSerializer(serializers.ModelSerializer):
    referee = UserProfileSerializer()

    class Meta:
        model = Referral
        fields = ('referee', 'referred_at')



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'body', 'created_on']
        read_only_fields = ['created_on']



    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)

        return contact
