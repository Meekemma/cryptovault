from django.db import models
from base.models import UserProfile
from django.db.models import Sum

# Create your models here.

class Referral(models.Model):

    BONUS_STATUS = (
    ('pending', 'Pending'),
    ('earned', 'Earned'),
    ('revoked', 'Revoked'),  

    )

    code = models.CharField(max_length=10, blank=True, null=True)
    referee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='referrals')  # the new user
    referrer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals_by_referrer')  # who referred them
    status = models.CharField(max_length=10, choices=BONUS_STATUS, default='pending')

    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    referred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral {self.code} by {self.referrer} for {self.referee}"
    
    class Meta:
        
        constraints = [
        models.UniqueConstraint(fields=['referee'], name='unique_referral_per_user')
        ]
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        ordering = ['-referred_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['referee']),
            models.Index(fields=['referrer']),
        ]


    @staticmethod
    def get_referee_count(referrer_profile):
        return Referral.objects.filter(referrer=referrer_profile).count()
    
    @staticmethod
    def get_referral_bonus(referrer_profile):
        return Referral.objects.filter(referrer=referrer_profile).aggregate(Sum('bonus'))['bonus__sum'] or 0.00
    

    @staticmethod
    def get_referees(referrer_profile):
        return Referral.objects.filter(referrer=referrer_profile)
    




class Contact(models.Model):
    name= models.CharField(max_length=200)
    email=models.EmailField()
    body=models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    class Meta:
        ordering = ['-created_on']


    def __str__(self):
        return self.name