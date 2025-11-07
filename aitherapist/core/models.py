from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Chat(models.Model):
    """Store chat conversations between user and AI"""
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    ai_response = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    confidence_score = models.FloatField(default=0.0)  # Sentiment confidence
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class MoodLog(models.Model):
    """Daily mood aggregation for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    positive_count = models.IntegerField(default=0)
    negative_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    total_chats = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"Mood log for {self.user.username} on {self.date}"
    
    @property
    def dominant_mood(self):
        """Returns the dominant mood for the day"""
        if self.positive_count >= self.negative_count and self.positive_count >= self.neutral_count:
            return 'positive'
        elif self.negative_count >= self.neutral_count:
            return 'negative'
        else:
            return 'neutral'
    
    @classmethod
    def update_or_create_daily_log(cls, user, sentiment):
        """Update or create daily mood log based on new chat sentiment"""
        today = timezone.now().date()
        log, created = cls.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_chats': 0
            }
        )
        
        # Increment the appropriate counter
        if sentiment == 'positive':
            log.positive_count += 1
        elif sentiment == 'negative':
            log.negative_count += 1
        else:
            log.neutral_count += 1
        
        log.total_chats += 1
        log.save()
        return log


class EmailVerificationOTP(models.Model):
    """OTP model for email verification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.email} - {self.otp_code}"
    
    def is_expired(self):
        """Check if OTP has expired (10 minutes)"""
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() > expiration_time
    
    @classmethod
    def generate_otp(cls, user, email):
        """Generate a new 6-digit OTP for the user"""
        # Delete any existing unverified OTPs for this user
        cls.objects.filter(user=user, is_verified=False).delete()
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Create new OTP record
        otp = cls.objects.create(
            user=user,
            email=email,
            otp_code=otp_code
        )
        return otp
    
    @classmethod
    def verify_otp(cls, user, otp_code):
        """Verify the OTP code for a user"""
        try:
            otp = cls.objects.filter(
                user=user,
                otp_code=otp_code,
                is_verified=False
            ).latest('created_at')
            
            if otp.is_expired():
                return False, "OTP has expired. Please request a new one."
            
            otp.is_verified = True
            otp.save()
            return True, "OTP verified successfully."
        except cls.DoesNotExist:
            return False, "Invalid OTP code. Please try again."
