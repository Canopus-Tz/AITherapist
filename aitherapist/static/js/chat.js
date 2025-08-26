// static/js/chat.js

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const messagesContainer = document.getElementById('messagesContainer');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const getCopingStrategyBtn = document.getElementById('getCopingStrategy');
    const clearChatBtn = document.getElementById('clearChat');
    
    // Initialize chat functionality
    initializeChat();
    
    function initializeChat() {
        // Auto-focus message input
        messageInput.focus();
        
        // Scroll to bottom of messages
        scrollToBottom();
        
        // Form submit handler
        chatForm.addEventListener('submit', handleMessageSubmit);
        
        // Enter key handler
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleMessageSubmit(e);
            }
        });
        
        // Coping strategy handler
        if (getCopingStrategyBtn) {
            getCopingStrategyBtn.addEventListener('click', showCopingStrategy);
        }
        
        // Clear chat handler
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', confirmClearChat);
        }
        
        // Auto-resize input
        messageInput.addEventListener('input', autoResizeInput);
    }
    
    async function handleMessageSubmit(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) {
            showError('Please enter a message');
            return;
        }
        
        // Disable form during sending
        setFormLoading(true);
        
        try {
            // Add user message to chat
            addUserMessage(message);
            
            // Clear input
            messageInput.value = '';
            autoResizeInput();
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send message to server
            const response = await sendMessageToServer(message);
            
            if (response.success) {
                // Hide typing indicator
                hideTypingIndicator();
                
                // Add AI response
                addAIMessage(response.ai_response, response.sentiment, response.timestamp);
                
                // Show success feedback
                showSuccessFeedback();
            } else {
                throw new Error(response.error || 'Failed to send message');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            showError('Sorry, there was an error sending your message. Please try again.');
        } finally {
            setFormLoading(false);
            messageInput.focus();
        }
    }
    
    async function sendMessageToServer(message) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/send-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    function addUserMessage(message) {
        const messageElement = createMessageElement('user', message, new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    function addAIMessage(message, sentiment, timestamp) {
        const messageElement = createMessageElement('ai', message, timestamp, sentiment);
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    function createMessageElement(sender, message, timestamp, sentiment = null) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper mb-3 fade-in-up';
        
        const isUser = sender === 'user';
        const alignClass = isUser ? 'justify-content-end' : '';
        const bgClass = isUser ? 'bg-primary text-white' : 'bg-light';
        const iconClass = isUser ? 'bi-person' : 'bi-robot';
        const iconBgClass = isUser ? 'bg-secondary' : 'bg-success';
        const orderClass = isUser ? 'me-3' : '';
        const maxWidthStyle = 'style="max-width: 70%;"';
        
        let sentimentBadge = '';
        if (sentiment && !isUser) {
            const sentimentInfo = getSentimentInfo(sentiment);
            sentimentBadge = `
                <small class="text-muted">
                    Mood: <span class="${sentimentInfo.class}">${sentimentInfo.label} ${sentimentInfo.icon}</span>
                </small>
            `;
        }
        
        wrapper.innerHTML = `
            <div class="d-flex align-items-start ${alignClass}">
                ${!isUser ? `
                    <div class="${iconBgClass} text-white rounded-circle p-2 me-3 flex-shrink-0">
                        <i class="bi ${iconClass}"></i>
                    </div>
                ` : ''}
                <div class="message-content ${bgClass} rounded p-3 ${orderClass} flex-grow-1" ${maxWidthStyle}>
                    <p class="mb-1">${formatMessage(message)}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="${isUser ? 'opacity-75' : 'text-muted'}">${timestamp}</small>
                        ${sentimentBadge}
                    </div>
                </div>
                ${isUser ? `
                    <div class="${iconBgClass} text-white rounded-circle p-2 flex-shrink-0">
                        <i class="bi ${iconClass}"></i>
                    </div>
                ` : ''}
            </div>
        `;
        
        return wrapper;
    }
    
    function getSentimentInfo(sentiment) {
        const sentimentMap = {
            'positive': { class: 'text-success', label: 'Positive', icon: '<i class="bi bi-emoji-smile"></i>' },
            'negative': { class: 'text-danger', label: 'Negative', icon: '<i class="bi bi-emoji-frown"></i>' },
            'neutral': { class: 'text-muted', label: 'Neutral', icon: '<i class="bi bi-emoji-neutral"></i>' }
        };
        return sentimentMap[sentiment] || sentimentMap['neutral'];
    }
    
    function formatMessage(message) {
        // Convert line breaks to <br> tags
        return message.replace(/\n/g, '<br>');
    }
    
    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
        scrollToBottom();
    }
    
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }
    
    function setFormLoading(loading) {
        sendButton.disabled = loading;
        messageInput.disabled = loading;
        
        if (loading) {
            sendButton.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        } else {
            sendButton.innerHTML = '<i class="bi bi-send"></i>';
        }
    }
    
    function scrollToBottom() {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
    
    function autoResizeInput() {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    }
    
    function showError(message) {
        // Create error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
        alertDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    function showSuccessFeedback() {
        // Subtle success feedback (could be a small animation or sound)
        sendButton.classList.add('btn-success');
        setTimeout(() => {
            sendButton.classList.remove('btn-success');
        }, 500);
    }
    
    async function showCopingStrategy() {
        const modal = new bootstrap.Modal(document.getElementById('copingStrategyModal'));
        const contentDiv = document.getElementById('copingStrategyContent');
        
        // Show modal with loading state
        modal.show();
        contentDiv.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Getting a personalized coping strategy for you...</p>
            </div>
        `;
        
        try {
            const response = await fetch('/api/coping-strategy/');
            const data = await response.json();
            
            contentDiv.innerHTML = `
                <div class="text-center mb-3">
                    <i class="bi bi-lightbulb-fill text-warning" style="font-size: 2rem;"></i>
                </div>
                <div class="strategy-content">
                    ${data.strategy.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
                </div>
            `;
            
        } catch (error) {
            console.error('Error fetching coping strategy:', error);
            contentDiv.innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-circle mb-2" style="font-size: 2rem;"></i>
                    <p>Sorry, we couldn't load a coping strategy right now. Please try again later.</p>
                </div>
            `;
        }
    }
    
    function confirmClearChat() {
        if (confirm('Are you sure you want to clear this chat session? This will only clear the current view, your chat history will still be saved.')) {
            // Clear current chat messages (but keep welcome message)
            const userMessages = chatMessages.querySelectorAll('.message-wrapper:not(:first-child)');
            userMessages.forEach(msg => msg.remove());
            
            // Show confirmation
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
            alertDiv.innerHTML = `
                <i class="bi bi-check-circle me-2"></i>Chat cleared successfully!
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(alertDiv);
            setTimeout(() => alertDiv.remove(), 3000);
        }
    }
    
    // Handle "Get Another" strategy button
    document.getElementById('getAnotherStrategy')?.addEventListener('click', showCopingStrategy);
    
    // Handle chat history item clicks
    document.querySelectorAll('.chat-history-item').forEach(item => {
        item.addEventListener('click', function() {
            // Add visual feedback
            document.querySelectorAll('.chat-history-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // You could implement loading specific chat history here
            // For now, just provide feedback
            const chatId = this.getAttribute('data-chat-id');
            console.log('Loading chat:', chatId);
        });
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        scrollToBottom();
    });
    
    // Handle visibility change (when user comes back to tab)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            messageInput.focus();
        }
    });
    
    // Add some nice touch interactions for mobile
    if ('ontouchstart' in window) {
        messageInput.addEventListener('touchstart', function() {
            setTimeout(() => {
                scrollToBottom();
            }, 300);
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + / to focus message input
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            messageInput.focus();
        }
        
        // Escape to clear message input
        if (e.key === 'Escape' && document.activeElement === messageInput) {
            messageInput.value = '';
            autoResizeInput();
        }
    });
});

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}