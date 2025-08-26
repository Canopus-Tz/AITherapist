# core/ai_therapist.py
import torch
from transformers import pipeline
import random
import logging

logger = logging.getLogger(__name__)


class AITherapist:
    """AI Therapist class for sentiment analysis and response generation"""
    
    def __init__(self):
        try:
            # Load sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )
            logger.info("Sentiment analyzer loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment analyzer: {e}")
            self.sentiment_analyzer = None
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of user message
        Returns: (sentiment, confidence_score)
        """
        if not self.sentiment_analyzer:
            return 'neutral', 0.5
        
        try:
            results = self.sentiment_analyzer(text)[0]
            
            # Convert results to our format
            sentiment_map = {'POSITIVE': 'positive', 'NEGATIVE': 'negative'}
            
            # Find the highest scoring sentiment
            best_result = max(results, key=lambda x: x['score'])
            sentiment = sentiment_map.get(best_result['label'], 'neutral')
            confidence = best_result['score']
            
            return sentiment, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 'neutral', 0.5
    
    def generate_response(self, user_message, sentiment, confidence):
        """
        Generate empathetic AI response based on sentiment
        """
        responses = self._get_response_templates()
        
        # Select appropriate responses based on sentiment
        if sentiment in responses:
            response_list = responses[sentiment]
        else:
            response_list = responses['neutral']
        
        # Add confidence-based modifiers
        if confidence < 0.6:
            # Low confidence - use neutral, supportive language
            response_list = responses['neutral']
        
        # Select random response and personalize
        base_response = random.choice(response_list)
        
        # Add personalized touch based on keywords in user message
        personalized_response = self._personalize_response(base_response, user_message, sentiment)
        
        return personalized_response
    
    def _get_response_templates(self):
        """Response templates categorized by sentiment"""
        return {
            'positive': [
                "That's wonderful to hear! 😊 It sounds like you're having a good experience. What's been going particularly well for you?",
                "I'm so glad you're feeling positive! 🌟 Celebrating these moments is important. How can we build on this feeling?",
                "It's great that you're sharing something positive with me! These moments of joy are precious. What made this especially meaningful for you?",
                "Your positive energy is lovely! ✨ It's beautiful when we can appreciate the good things in life. Tell me more about what's bringing you happiness.",
                "That sounds really encouraging! 🙂 I love hearing when things are going well. What would you like to focus on to maintain this positive momentum?"
            ],
            'negative': [
                "I hear you, and I want you to know that what you're feeling is valid. 💙 Difficult emotions can be really challenging. Would you like to talk more about what's troubling you?",
                "That sounds really tough, and I'm sorry you're going through this. 🤗 Sometimes just expressing these feelings can help. What support do you need right now?",
                "I can sense that you're struggling, and that takes courage to share. 💪 You don't have to go through this alone. What would feel most helpful for you in this moment?",
                "It sounds like you're carrying some heavy feelings right now. 💛 Remember that it's okay to not be okay. Would you like to explore some coping strategies together?",
                "I'm here to listen and support you through this difficult time. 🫂 Your feelings matter, and so do you. What's been the hardest part about this situation?"
            ],
            'neutral': [
                "Thank you for sharing that with me. 💭 I'm here to listen and support you. What's on your mind today?",
                "I appreciate you taking the time to talk with me. 🌸 Every conversation matters. How are you feeling right now?",
                "It's good that you're here and willing to open up. 🤝 That shows strength. What would you like to focus on in our conversation?",
                "I'm glad you felt comfortable sharing that. 💬 Sometimes talking things through can bring clarity. What's been occupying your thoughts lately?",
                "Thank you for trusting me with your thoughts. 🌿 I'm here to support you however I can. What feels most important to discuss right now?"
            ]
        }
    
    def _personalize_response(self, base_response, user_message, sentiment):
        """Add personalization based on user message content"""
        user_message_lower = user_message.lower()
        
        # Add specific suggestions based on keywords
        suggestions = []
        
        if any(word in user_message_lower for word in ['stress', 'stressed', 'overwhelmed', 'pressure']):
            suggestions.extend([
                "\n\n💡 Here's a quick stress-relief technique: Try the 4-7-8 breathing method - inhale for 4 counts, hold for 7, exhale for 8.",
                "\n\n🧘‍♀️ When feeling overwhelmed, try grounding yourself: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste."
            ])
        
        if any(word in user_message_lower for word in ['anxious', 'anxiety', 'worried', 'nervous']):
            suggestions.extend([
                "\n\n🌱 For anxiety, try this: Focus on your breath and remind yourself 'This feeling will pass.' You're stronger than you know.",
                "\n\n💙 Anxiety can feel overwhelming, but remember: you've handled difficult situations before, and you can handle this too."
            ])
        
        if any(word in user_message_lower for word in ['sad', 'depressed', 'down', 'lonely']):
            suggestions.extend([
                "\n\n🌈 When feeling down, small acts of self-care can help: a warm cup of tea, a short walk, or calling someone you care about.",
                "\n\n🤗 Remember that sadness is a natural emotion, and it's okay to feel this way. You matter, and this feeling is temporary."
            ])
        
        if any(word in user_message_lower for word in ['work', 'job', 'career', 'boss']):
            suggestions.append("\n\n💼 Work challenges can be tough. Remember to set boundaries and take breaks when possible.")
        
        if any(word in user_message_lower for word in ['relationship', 'friend', 'family', 'partner']):
            suggestions.append("\n\n💕 Relationships can be complex. Open, honest communication often helps, and remember that your feelings are valid.")
        
        # Add a random suggestion if applicable
        if suggestions:
            base_response += random.choice(suggestions)
        
        return base_response
    
    def get_coping_strategies(self, sentiment_type=None):
        """Get coping strategies based on sentiment type"""
        strategies = {
            'stress': [
                "🧘‍♀️ **Deep Breathing**: Inhale slowly for 4 counts, hold for 4, exhale for 6. Repeat 5 times.",
                "🚶‍♀️ **Take a Walk**: Even 5 minutes of movement can help clear your mind.",
                "📝 **Brain Dump**: Write down everything you're thinking about for 10 minutes without editing.",
                "🎵 **Listen to Music**: Choose something that matches your mood, then gradually shift to more uplifting songs."
            ],
            'anxiety': [
                "🌍 **5-4-3-2-1 Technique**: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
                "💭 **Question Your Thoughts**: Ask yourself 'Is this thought helpful? Is it likely to happen? What would I tell a friend?'",
                "🤗 **Self-Compassion**: Speak to yourself as you would to a dear friend going through the same thing.",
                "📱 **Progressive Muscle Relaxation**: Tense and release each muscle group for 5 seconds, starting from your toes."
            ],
            'sadness': [
                "☀️ **Gentle Movement**: Try some light stretching or yoga to help shift your energy.",
                "💌 **Write a Letter**: Write to yourself with kindness, or to someone you care about (you don't have to send it).",
                "🌱 **Small Accomplishments**: Do one tiny task that makes you feel productive, like making your bed or organizing one drawer.",
                "🎨 **Creative Expression**: Draw, color, sing, or create something - it doesn't need to be 'good'."
            ],
            'general': [
                "☕ **Mindful Moments**: Spend 2 minutes fully focused on one activity - drinking tea, feeling sunshine, etc.",
                "📚 **Gratitude Practice**: Write down 3 small things you're grateful for today.",
                "🌸 **Self-Care Check**: Ask yourself what you need right now - rest, nutrition, connection, or movement?",
                "📞 **Reach Out**: Consider talking to a friend, family member, or mental health professional."
            ]
        }
        
        if sentiment_type and sentiment_type in strategies:
            return random.choice(strategies[sentiment_type])
        else:
            return random.choice(strategies['general'])


# Singleton instance
ai_therapist = AITherapist()