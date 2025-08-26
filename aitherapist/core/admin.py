from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Chat, MoodLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_full_name', 'created_at', 'has_avatar']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    
    def get_full_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    get_full_name.short_description = 'Full Name'
    
    def has_avatar(self, obj):
        if obj.avatar:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_avatar.short_description = 'Avatar'


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_message_preview', 'sentiment', 'confidence_score', 'timestamp']
    list_filter = ['sentiment', 'timestamp', 'confidence_score']
    search_fields = ['user__username', 'user_message', 'ai_response']
    readonly_fields = ['timestamp', 'confidence_score']
    date_hierarchy = 'timestamp'
    
    def get_message_preview(self, obj):
        return obj.user_message[:50] + "..." if len(obj.user_message) > 50 else obj.user_message
    get_message_preview.short_description = 'Message Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# ✅ Custom filter for dominant_mood (since it's a property, not a DB field)
class DominantMoodFilter(admin.SimpleListFilter):
    title = 'Dominant Mood'
    parameter_name = 'dominant_mood'

    def lookups(self, request, model_admin):
        return [
            ('positive', 'Positive'),
            ('negative', 'Negative'),
            ('neutral', 'Neutral'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return [obj for obj in queryset if obj.dominant_mood == value]
        return queryset


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_chats', 'positive_count', 'negative_count', 'neutral_count', 'dominant_mood']
    list_filter = ['date', DominantMoodFilter]  # ✅ fixed
    search_fields = ['user__username']
    readonly_fields = ['dominant_mood']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Customize admin site header
admin.site.site_header = "AI Therapist Administration"
admin.site.site_title = "AI Therapist Admin"
admin.site.index_title = "Welcome to AI Therapist Administration"
