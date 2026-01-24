// static/js/dashboard.js

// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    
    // Wait for Chart.js to be available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    } else {
        // If Chart.js is not loaded yet, wait a bit and try again
        setTimeout(function() {
            if (typeof Chart !== 'undefined') {
                initializeCharts();
            } else {
                console.error('Chart.js is not loaded. Please check if the CDN link is working.');
            }
        }, 100);
    }
});

function initializeDashboard() {
    // Initialize any dashboard-specific functionality
    setupInteractiveElements();
    setupAnimations();
}

function initializeCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not available');
        return;
    }
    
    // Initialize Mood Trend Chart
    initializeMoodTrendChart();
    
    // Initialize Mood Distribution Chart
    initializeMoodDistributionChart();
}

function initializeMoodTrendChart() {
    const ctx = document.getElementById('moodTrendChart');
    if (!ctx) {
        console.warn('Mood trend chart canvas not found');
        return;
    }
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not available');
        return;
    }
    
    const chartData = window.chartData || [];
    
    // Debug: Log chart data
    console.log('Chart Data:', chartData);
    
    // If no data, show empty state message
    if (chartData.length === 0) {
        const cardBody = ctx.closest('.card-body');
        if (cardBody) {
            cardBody.innerHTML = '<div class="text-center text-muted py-5"><i class="bi bi-graph-up d-block mb-2" style="font-size: 2rem;"></i><p class="mb-0">No data available yet.<br>Start chatting to see your mood trends!</p></div>';
        }
        return;
    }
    
    // FIXED: Set canvas dimensions to match container
    const container = ctx.closest('.chart-container');
    if (container) {
        ctx.width = container.clientWidth - 32; // Subtract padding (1rem * 2)
        ctx.height = container.clientHeight - 32;
    }
    
    // Prepare data for the chart
    const labels = chartData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const positiveData = chartData.map(item => item.positive || 0);
    const negativeData = chartData.map(item => item.negative || 0);
    const neutralData = chartData.map(item => item.neutral || 0);
    
    try {
        new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Positive',
                    data: positiveData,
                    borderColor: 'rgb(25, 135, 84)',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Neutral',
                    data: neutralData,
                    borderColor: 'rgb(108, 117, 125)',
                    backgroundColor: 'rgba(108, 117, 125, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Negative',
                    data: negativeData,
                    borderColor: 'rgb(220, 53, 69)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
        });
        console.log('Mood trend chart initialized successfully');
    } catch (error) {
        console.error('Error initializing mood trend chart:', error);
    }
}

function initializeMoodDistributionChart() {
    const ctx = document.getElementById('moodDistributionChart');
    if (!ctx) {
        console.warn('Mood distribution chart canvas not found');
        return;
    }
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not available');
        return;
    }
    
    const totalStats = window.totalStats || { positive: 0, negative: 0, neutral: 0 };
    
    // Debug: Log stats
    console.log('Total Stats:', totalStats);
    
    // FIXED: Set canvas dimensions to match container
    const container = ctx.closest('.chart-container');
    if (container) {
        ctx.width = container.clientWidth - 32; // Subtract padding (1rem * 2)
        ctx.height = container.clientHeight - 32;
    }
    
    // Calculate total for percentage calculation
    const total = totalStats.positive + totalStats.negative + totalStats.neutral;
    
    // If no data, show empty state message in the card body instead
    if (total === 0) {
        const cardBody = ctx.closest('.card-body');
        if (cardBody) {
            cardBody.innerHTML = '<div class="text-center text-muted"><i class="bi bi-info-circle d-block mb-2" style="font-size: 2rem;"></i><p class="mb-0">No data available yet.<br>Start chatting to see your mood distribution!</p></div>';
        }
        return;
    }
    
    try {
        new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [totalStats.positive, totalStats.neutral, totalStats.negative],
                backgroundColor: [
                    'rgb(25, 135, 84)',
                    'rgb(108, 117, 125)',
                    'rgb(220, 53, 69)'
                ],
                borderColor: [
                    'rgb(25, 135, 84)',
                    'rgb(108, 117, 125)',
                    'rgb(220, 53, 69)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
        });
        console.log('Mood distribution chart initialized successfully');
    } catch (error) {
        console.error('Error initializing mood distribution chart:', error);
    }
}

function setupInteractiveElements() {
    // Add click handlers for insight cards
    const insightCards = document.querySelectorAll('.insight-card');
    insightCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add ripple effect
            createRippleEffect(this, event);
        });
    });
    
    // Add hover effects for recent chat items
    const recentChatItems = document.querySelectorAll('.recent-chat-item');
    recentChatItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
        
        item.addEventListener('click', function() {
            // Navigate to chat with context
            window.location.href = '/chat/';
        });
    });
    
    // Add interactive stats cards
    const statsCards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-warning, .card.bg-info');
    statsCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function setupAnimations() {
    // Animate stats on load
    animateCounters();
    
    // Animate insights cards
    const insightCards = document.querySelectorAll('.insight-card');
    insightCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, index * 200);
    });
}

function animateCounters() {
    const counters = document.querySelectorAll('.card h2');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
        if (isNaN(target)) return;
        
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            // Handle percentage signs
            if (counter.textContent.includes('%')) {
                counter.textContent = Math.floor(current) + '%';
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 30);
    });
}

function createRippleEffect(element, event) {
    const ripple = document.createElement('div');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        0% {
            transform: scale(0);
            opacity: 1;
        }
        100% {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export functions for use in templates
window.dashboardUtils = {
    createRippleEffect,
    animateCounters
};