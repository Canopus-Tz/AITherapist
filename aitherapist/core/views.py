# core/views.py
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User

from .forms import CustomUserCreationForm, UserProfileForm, ChatMessageForm
from .models import UserProfile, Chat, MoodLog, EmailVerificationOTP
from .ai_therapist import ai_therapist
from .email_utils import send_otp_email


def home(request):
    """Home page - redirect authenticated users to chat"""
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'core/home.html')


class CustomLoginView(LoginView):
    """Custom login view with redirect"""
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/chat/'

def register_view(request):
    """User registration view - sends OTP for email verification"""
    if request.user.is_authenticated:
        return redirect('chat')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            # Generate and send OTP
            otp = EmailVerificationOTP.generate_otp(user, email)
            
            # Send OTP email
            if send_otp_email(user, email, otp.otp_code):
                messages.success(request, f'Account created for {username}! Please check your email for the verification code.')
                # Store user ID in session for OTP verification
                request.session['pending_verification_user_id'] = user.id
                return redirect('verify_otp')
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
                user.delete()  # Delete user if email sending fails
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})


def verify_otp_view(request):
    """OTP verification view - verifies email OTP and logs in user"""
    # Check if user is already authenticated
    if request.user.is_authenticated:
        return redirect('chat')
    
    # Check if there's a pending verification user in session
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.error(request, 'No pending verification found. Please register again.')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        request.session.pop('pending_verification_user_id', None)
        return redirect('register')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code or len(otp_code) != 6:
            messages.error(request, 'Please enter a valid 6-digit OTP code.')
            return render(request, 'core/verify_otp.html', {'user': user})
        
        # Verify OTP
        is_valid, message = EmailVerificationOTP.verify_otp(user, otp_code)
        
        if is_valid:
            # Clear session
            request.session.pop('pending_verification_user_id', None)
            
            # Log in the user
            login(request, user)
            messages.success(request, 'Email verified successfully! Welcome to AI Therapist.')
            return redirect('chat')
        else:
            messages.error(request, message)
            return render(request, 'core/verify_otp.html', {'user': user})
    
    # GET request - show OTP input form
    return render(request, 'core/verify_otp.html', {'user': user})


@require_POST
def resend_otp_view(request):
    """Resend OTP verification code"""
    # Check if user is already authenticated
    if request.user.is_authenticated:
        return redirect('chat')
    
    # Check if there's a pending verification user in session
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.error(request, 'No pending verification found. Please register again.')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        request.session.pop('pending_verification_user_id', None)
        return redirect('register')
    
    # Generate and send new OTP
    otp = EmailVerificationOTP.generate_otp(user, user.email)
    
    if send_otp_email(user, user.email, otp.otp_code):
        messages.success(request, 'A new verification code has been sent to your email.')
    else:
        messages.error(request, 'Failed to send verification email. Please try again.')
    
    return redirect('verify_otp')


@require_POST
@login_required
def logout_view(request):
    """Logout view - logs out user and redirects to home"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')    


@login_required
def chat_view(request):
    """Main chat interface"""
    # Get recent chats for this user
    recent_chats = Chat.objects.filter(user=request.user)[:20]
    form = ChatMessageForm()
    
    context = {
        'recent_chats': recent_chats,
        'form': form,
    }
    return render(request, 'core/chat.html', context)


@login_required
@require_POST
def send_message(request):
    """Handle AJAX chat message sending"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Analyze sentiment
        sentiment, confidence = ai_therapist.analyze_sentiment(user_message)
        
        # Generate AI response
        ai_response = ai_therapist.generate_response(user_message, sentiment, confidence)
        
        # Save chat to database
        chat = Chat.objects.create(
            user=request.user,
            user_message=user_message,
            ai_response=ai_response,
            sentiment=sentiment,
            confidence_score=confidence
        )
        
        # Update mood log
        MoodLog.update_or_create_daily_log(request.user, sentiment)
        
        # Return response
        return JsonResponse({
            'success': True,
            'ai_response': ai_response,
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'timestamp': chat.timestamp.strftime('%H:%M')
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard_view(request):
    """Dashboard with mood analytics"""
    # Get date range (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get mood logs for the period
    mood_logs = MoodLog.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Prepare data for charts
    chart_data = []
    total_stats = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
    
    for log in mood_logs:
        chart_data.append({
            'date': log.date.strftime('%Y-%m-%d'),
            'positive': log.positive_count,
            'negative': log.negative_count,
            'neutral': log.neutral_count,
            'total': log.total_chats
        })
        
        total_stats['positive'] += log.positive_count
        total_stats['negative'] += log.negative_count
        total_stats['neutral'] += log.neutral_count
        total_stats['total'] += log.total_chats
    
    # Get recent chats
    recent_chats = Chat.objects.filter(user=request.user)[:10]
    
    # Calculate weekly summary
    week_ago = end_date - timedelta(days=7)
    weekly_logs = MoodLog.objects.filter(
        user=request.user,
        date__gte=week_ago
    )
    
    weekly_stats = {
        'positive': sum(log.positive_count for log in weekly_logs),
        'negative': sum(log.negative_count for log in weekly_logs),
        'neutral': sum(log.neutral_count for log in weekly_logs),
        'total': sum(log.total_chats for log in weekly_logs),
    }
    
    # Calculate mood percentage
    if total_stats['total'] > 0:
        mood_percentages = {
            'positive': round((total_stats['positive'] / total_stats['total']) * 100, 1),
            'negative': round((total_stats['negative'] / total_stats['total']) * 100, 1),
            'neutral': round((total_stats['neutral'] / total_stats['total']) * 100, 1),
        }
    else:
        mood_percentages = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    # Generate insights
    insights = generate_insights(request.user, weekly_stats, total_stats, mood_logs)
    
    context = {
        'chart_data': json.dumps(chart_data),
        'total_stats': total_stats,
        'weekly_stats': weekly_stats,
        'mood_percentages': mood_percentages,
        'recent_chats': recent_chats,
        'insights': insights,
        'days_tracked': len(chart_data),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def deleteAcc_view(request):
    """Delete account view - shows confirmation on GET, deletes on POST"""
    if request.method == 'POST':
        user = request.user
        username = user.username
        
        # Delete the user (this will cascade delete related data if models are set up correctly)
        user.delete()
        
        # Logout the user (though user is already deleted, this clears the session)
        logout(request)
        
        messages.success(request, f'Account "{username}" has been deleted successfully.')
        return redirect('home')
    
    # GET request - show confirmation page
    return render(request, 'core/delete_account_confirm.html')


@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Get user statistics
    total_chats = Chat.objects.filter(user=request.user).count()
    days_active = MoodLog.objects.filter(user=request.user).count()
    
    context = {
        'form': form,
        'profile': profile,
        'total_chats': total_chats,
        'days_active': days_active,
    }
    return render(request, 'core/profile.html', context)


@login_required
def get_coping_strategy(request):
    """AJAX endpoint to get coping strategies"""
    strategy_type = request.GET.get('type', 'general')
    strategy = ai_therapist.get_coping_strategies(strategy_type)
    
    return JsonResponse({
        'strategy': strategy,
        'type': strategy_type
    })


def generate_insights(user, weekly_stats, total_stats, mood_logs):
    """Generate personalized insights for the user"""
    insights = []
    
    if total_stats['total'] == 0:
        insights.append({
            'type': 'welcome',
            'title': 'Welcome to AI Therapist! 🌟',
            'message': 'Start your mental health journey by having your first conversation with our AI therapist.',
            'icon': 'bi-chat-heart'
        })
        return insights
    
    # Weekly activity insight
    if weekly_stats['total'] > 0:
        dominant_weekly_mood = max(weekly_stats, key=lambda k: weekly_stats[k] if k != 'total' else 0)
        if dominant_weekly_mood != 'total':
            insights.append({
                'type': 'weekly',
                'title': f'This Week\'s Mood Trend',
                'message': f'You\'ve been mostly {dominant_weekly_mood} this week with {weekly_stats["total"]} conversations. Keep up the great work on self-reflection!',
                'icon': 'bi-calendar-week'
            })
    
    # Positive trend insight
    if total_stats['positive'] > total_stats['negative']:
        insights.append({
            'type': 'positive',
            'title': 'Positive Outlook! 😊',
            'message': f'Great news! {round((total_stats["positive"]/total_stats["total"])*100)}% of your conversations have been positive. You\'re doing amazing!',
            'icon': 'bi-emoji-smile'
        })
    
    # Consistency insight
    if len(mood_logs) >= 7:
        recent_logs = mood_logs[-7:]  # Last 7 days
        active_days = len([log for log in recent_logs if log.total_chats > 0])
        if active_days >= 5:
            insights.append({
                'type': 'consistency',
                'title': 'Consistency Champion! 🏆',
                'message': f'You\'ve been active {active_days} out of the last 7 days. Regular check-ins are key to mental wellness!',
                'icon': 'bi-trophy'
            })
    
    # Growth insight
    if len(mood_logs) >= 14:
        first_week = mood_logs[:7]
        last_week = mood_logs[-7:]
        
        first_week_positive = sum(log.positive_count for log in first_week)
        last_week_positive = sum(log.positive_count for log in last_week)
        
        if last_week_positive > first_week_positive:
            insights.append({
                'type': 'growth',
                'title': 'Positive Growth! 📈',
                'message': 'Your positive conversations have increased compared to earlier. You\'re making great progress!',
                'icon': 'bi-graph-up-arrow'
            })
    
    # Support insight for negative trends
    if total_stats['negative'] > total_stats['positive'] and total_stats['total'] >= 5:
        insights.append({
            'type': 'support',
            'title': 'We\'re Here for You 💙',
            'message': 'It seems like you\'ve been going through some challenges. Remember, it\'s okay to not be okay. Consider reaching out to a professional counselor for additional support.',
            'icon': 'bi-heart'
        })
    
    # Engagement milestone
    milestones = [10, 25, 50, 100, 200]
    for milestone in milestones:
        if total_stats['total'] == milestone:
            insights.append({
                'type': 'milestone',
                'title': f'Milestone Achieved! 🎉',
                'message': f'Congratulations! You\'ve had {milestone} conversations with our AI therapist. Your commitment to mental health is inspiring!',
                'icon': 'bi-award'
            })
            break
    
    return insights[:4]  # Limit to 4 insights