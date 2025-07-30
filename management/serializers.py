from rest_framework import serializers
from .models import Referral,Contact
from base.models import UserProfile





class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= UserProfile
        fields = ['first_name', 'last_name', 'email']
        read_only_fields = ['first_name', 'last_name', 'email', ]



class ReferralSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, required=True)  
    referee_count = serializers.SerializerMethodField()
    referral_bonus = serializers.SerializerMethodField()
    referee_details = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = [
            'code', 'referee', 'referrer', 'status', 'bonus', 'referred_at',
            'referee_count', 'referral_bonus', 'referee_details'
        ]
        read_only_fields = [
            'referee', 'referrer', 'status', 'bonus', 'referred_at',
            'referee_count', 'referral_bonus', 'referees'
        ]

    def get_referee_count(self, obj):
        if not obj.referrer:
            return 0
        return Referral.get_referee_count(obj.referrer)

    def get_referral_bonus(self, obj):
        if not obj.referrer:
            return 0.00
        return Referral.get_referral_bonus(obj.referrer)

    def get_referee_details(self, obj):
        # Return details for the specific referee of this referral
        if not obj.referee:
            return {}
        return {
            'email': obj.referee.user.email,
            'full_name': f"{obj.referee.user.first_name} {obj.referee.user.last_name}",
            'status': obj.status,
            'bonus': obj.bonus,
            'referred_at': obj.referred_at,
        }


    def validate_code(self, value):
        try:
            referrer_profile = UserProfile.objects.get(referral_code=value)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("This referral code does not exist.")
        
        self.context['referrer_profile'] = referrer_profile
        return value

    def create(self, validated_data):
        referrer_profile = self.context.get('referrer_profile')
        referee_profile = self.context.get('referee_profile')

        if referee_profile == referrer_profile:
            raise serializers.ValidationError("You cannot refer yourself.")

        if Referral.objects.filter(referee=referee_profile).exists():
            raise serializers.ValidationError("This user has already been referred.")

        referral = Referral.objects.create(
            code=validated_data['code'],
            referrer=referrer_profile,
            referee=referee_profile,
            status='pending',
            bonus=0.00,
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
