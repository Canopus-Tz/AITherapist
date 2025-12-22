// static/js/chat.js

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const messagesContainer = document.getElementById('messagesContainer');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const getCopingStrategyBtn = document.getElementById('getCopingStrategy');
    const newChatBtn = document.getElementById('newChatBtn');
    const clearChatBtn = document.getElementById('clearChat');
    const mainColumn = document.querySelector('.chat-main-column');
    let currentConversationId = mainColumn?.dataset?.conversationId || null;
    
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
        
        // New chat handler
        if (newChatBtn) {
            newChatBtn.addEventListener('click', startNewChat);
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
                
                // Update current conversation id if server returned one
                if (response.conversation_id) {
                    currentConversationId = response.conversation_id;
                    if (mainColumn) mainColumn.dataset.conversationId = response.conversation_id;
                }

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
        
        const payload = { message: message };
        if (currentConversationId) payload.conversation_id = currentConversationId;
        
        const response = await fetch('/send-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(payload)
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
    
    function escapeHtml(unsafe) {
        return unsafe
             .replace(/&/g, '&amp;')
             .replace(/</g, '&lt;')
             .replace(/>/g, '&gt;')
             .replace(/"/g, '&quot;')
             .replace(/'/g, '&#039;');
    }

    function formatMessage(message) {
        let cleaned = String(message).replace(/\{\{.*?\}\}/g, '');
        return escapeHtml(cleaned).replace(/\n/g, '<br>');
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
    
    // Create modal instance once and reuse it
    const modalElement = document.getElementById('copingStrategyModal');
    let copingStrategyModal = null;
    
    // Function to clean up duplicate modal backdrops
    function cleanupModalBackdrops() {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        // Keep only the first backdrop, remove the rest
        if (backdrops.length > 1) {
            for (let i = 1; i < backdrops.length; i++) {
                backdrops[i].remove();
            }
        }
    }
    
    // Initialize modal instance and set up backdrop cleanup
    if (modalElement) {
        copingStrategyModal = bootstrap.Modal.getOrCreateInstance(modalElement);
        
        // Clean up duplicate backdrops whenever modal is shown
        modalElement.addEventListener('shown.bs.modal', function() {
            cleanupModalBackdrops();
        });
        
        // Also clean up on hidden event
        modalElement.addEventListener('hidden.bs.modal', function() {
            cleanupModalBackdrops();
        });
        
        // Use MutationObserver to watch for new backdrop creation and remove duplicates immediately
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && node.classList && node.classList.contains('modal-backdrop')) {
                            // New backdrop was added, clean up duplicates
                            setTimeout(cleanupModalBackdrops, 10);
                        }
                    });
                }
            });
        });
        
        // Observe the body for backdrop additions
        observer.observe(document.body, {
            childList: true,
            subtree: false
        });
    }
    
    async function showCopingStrategy() {
        const contentDiv = document.getElementById('copingStrategyContent');
        
        // Ensure modal instance exists
        if (!copingStrategyModal && modalElement) {
            copingStrategyModal = bootstrap.Modal.getOrCreateInstance(modalElement);
        }
        
        // Check if modal is already visible
        const isModalVisible = modalElement && modalElement.classList.contains('show');
        
        // Show loading state immediately
        contentDiv.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Getting a personalized coping strategy for you...</p>
            </div>
        `;
        
        // Only show modal if it's not already visible
        if (!isModalVisible && copingStrategyModal) {
            copingStrategyModal.show();
            // Clean up backdrops after a short delay to ensure they're created
            setTimeout(cleanupModalBackdrops, 100);
        } else {
            // If modal is already visible, just clean up any duplicate backdrops
            cleanupModalBackdrops();
        }
        
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
    
    async function startNewChat() {
        // Ask server to create a new conversation and redirect
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        try {
            const resp = await fetch('/chat/new/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({})
            });
            const data = await resp.json();
            if (data.success && data.redirect_url) {
                window.location.href = data.redirect_url;
                return;
            }
        } catch (err) {
            console.error('Failed to start new chat', err);
        }

        // Fallback: clear UI only
        const messages = chatMessages.querySelectorAll('.message-wrapper');
        // Keep the first one (welcome message)
        for (let i = 1; i < messages.length; i++) {
            messages[i].remove();
        }

        // Optional: Reset active state in sidebar
        document.querySelectorAll('.chat-history-item').forEach(i => i.classList.remove('active'));

        // Focus input
        messageInput.value = '';
        autoResizeInput();
        messageInput.focus();

        // Feedback
        showSuccessFeedback();
    }

    async function confirmClearChat() {
        if (!confirm('Are you sure you want to clear this chat session? This will delete the conversation and its history.')) return;

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        try {
            const resp = await fetch('/chat/clear/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ conversation_id: currentConversationId })
            });
            const data = await resp.json();
            if (data.success && data.redirect_url) {
                window.location.href = data.redirect_url;
                return;
            }
        } catch (err) {
            console.error('Failed to clear chat', err);
        }

        // Fallback: local clear
        startNewChat();
    }
    
    // Handle "Get Another" strategy button
    document.getElementById('getAnotherStrategy')?.addEventListener('click', showCopingStrategy);
    
    // Handle chat history item clicks (redirect to conversation)
    document.querySelectorAll('.chat-history-item').forEach(item => {
        item.addEventListener('click', function() {
            // Add visual feedback
            document.querySelectorAll('.chat-history-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            const convId = this.getAttribute('data-conv-id');
            if (convId) {
                window.location.href = `/chat/?conversation=${convId}`;
            }
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