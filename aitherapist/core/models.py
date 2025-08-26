from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
