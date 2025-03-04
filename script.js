// Configuration
let API_URL = 'http://localhost:5000/api/chat';  // Default to localhost
const API_KEY = 'default-api-key-for-development';

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const queryInput = document.getElementById('query-input');
const sendButton = document.getElementById('send-button');
const englishBtn = document.getElementById('en-btn');
const hindiBtn = document.getElementById('hi-btn');
const examplesContainer = document.getElementById('examples-container');

// Application State
let currentLanguage = 'en';

// Example questions
const examples = {
    en: [
        "How do I file an FIR?",
        "What are my rights as a tenant?",
        "How can I get legal aid?",
        "What is the procedure for divorce?",
        "What are my property inheritance rights?"
    ],
    hi: [
        "मैं FIR कैसे दर्ज करूं?",
        "किरायेदार के रूप में मेरे क्या अधिकार हैं?",
        "मुझे कानूनी सहायता कैसे मिल सकती है?",
        "तलाक की प्रक्रिया क्या है?",
        "मेरे संपत्ति विरासत अधिकार क्या हैं?"
    ]
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateLanguage('en');
    queryInput.focus();
});

// Update API URL if ngrok is detected
function updateApiUrlForNgrok() {
    // Look for ngrok in the current URL
    if (window.location.hostname.includes('ngrok')) {
        // If we're on ngrok, construct the API URL with the same host but different path
        API_URL = `${window.location.protocol}//${window.location.host}/api/chat`;
        console.log('Detected ngrok, updated API URL to:', API_URL);
    }
}
updateApiUrlForNgrok();

// Language toggle
englishBtn.addEventListener('click', () => updateLanguage('en'));
hindiBtn.addEventListener('click', () => updateLanguage('hi'));

// Send message on click or pressing Enter
sendButton.addEventListener('click', sendMessage);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Update UI based on selected language
function updateLanguage(lang) {
    currentLanguage = lang;
    
    // Update active button
    englishBtn.classList.toggle('active', lang === 'en');
    hindiBtn.classList.toggle('active', lang === 'hi');
    
    // Update placeholder text
    if (lang === 'hi') {
        queryInput.placeholder = "कानूनी प्रश्न पूछें...";
        sendButton.title = "भेजें";
    } else {
        queryInput.placeholder = "Ask a legal question...";
        sendButton.title = "Send";
    }
    
    // Update examples
    updateExamples(lang);
}

// Update example questions based on language
function updateExamples(lang) {
    examplesContainer.innerHTML = '';
    examples[lang].forEach(example => {
        const button = document.createElement('button');
        button.className = 'example-button';
        button.textContent = example;
        button.addEventListener('click', () => {
            queryInput.value = example;
            sendMessage();
        });
        examplesContainer.appendChild(button);
    });
}

// Add a message to the chat
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const paragraph = document.createElement('p');
    paragraph.textContent = text;
    
    contentDiv.appendChild(paragraph);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to the bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Add thinking indicator
function addThinkingIndicator() {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'thinking';
    thinkingDiv.textContent = currentLanguage === 'hi' ? 'सोच रहा हूँ...' : 'Thinking...';
    chatContainer.appendChild(thinkingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return thinkingDiv;
}

// Send message to the API
async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;
    
    // Add user message to the chat
    addMessage(query, true);
    queryInput.value = '';
    queryInput.focus();
    
    // Add thinking indicator
    const thinkingDiv = addThinkingIndicator();
    
    try {
        // Send request to the API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({ query })
        });
        
        // Remove thinking indicator
        chatContainer.removeChild(thinkingDiv);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage(data.response);
        
    } catch (error) {
        console.error('Error:', error);
        chatContainer.removeChild(thinkingDiv);
        
        // Show error message based on language
        const errorMsg = currentLanguage === 'hi' 
            ? 'क्षमा करें, कोई त्रुटि हुई। कृपया बाद में पुनः प्रयास करें।' 
            : 'Sorry, an error occurred. Please try again later.';
        
        addMessage(errorMsg);
    }
}