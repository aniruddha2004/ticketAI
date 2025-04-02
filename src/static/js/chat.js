document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const ticketList = document.getElementById('ticket-list');
    
    let currentTicketId = null;
    let isChatActive = false;
    let ticketSummary = null;

    // Start a new chat conversation
    function startNewChat() {
        // Clear chat area
        chatMessages.innerHTML = '';
        isChatActive = true;
        
        // Make API request to start chat
        fetch('/api/chat/start')
            .then(response => response.json())
            .then(data => {
                // Display welcome message
                appendBotMessage(data.message);
            })
            .catch(error => {
                console.error('Error starting chat:', error);
                appendSystemMessage('An error occurred. Please try again.');
            });
    }

    // Load an existing ticket conversation
    function loadTicket(ticketId) {
        if (currentTicketId === ticketId) return;
        
        currentTicketId = ticketId;
        isChatActive = false;
        
        // Clear chat area
        chatMessages.innerHTML = '';
        
        // Make API request to get ticket details
        fetch(`/api/tickets/${ticketId}`)
            .then(response => response.json())
            .then(data => {
                // Display ticket information
                appendSystemMessage(`Ticket #${data.id}: ${data.title}`);
                appendSystemMessage(`Status: ${data.status} | Category: ${data.category} | Priority: ${data.priority}`);
                
                // Display ticket messages
                // data.messages.forEach(message => {
                //     if (message.is_system) {
                //         appendSystemMessage(message.content);
                //     } else if (message.username === 'System') {
                //         appendBotMessage(message.content);
                //     } else {
                //         appendUserMessage(message.content);
                //     }
                // });
                
                // Update UI to show we're viewing a ticket
                document.querySelectorAll('.ticket-item').forEach(item => {
                    item.classList.remove('active');
                });
                document.querySelector(`.ticket-item[data-id="${ticketId}"]`).classList.add('active');
                
                // Update the chat header
                // document.getElementById('chat-title').textContent = `Ticket #${data.id}: ${data.title}`;
            })
            .catch(error => {
                console.error('Error loading ticket:', error);
                appendSystemMessage('An error occurred while loading this ticket.');
            });
    }

    // Append a user message to the chat
    function appendUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-user';
        messageDiv.textContent = message;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getCurrentTime();
        
        messageDiv.appendChild(timeDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        scrollToBottom();
    }

    // Append a bot message to the chat
    function appendBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-bot';
        messageDiv.textContent = message;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getCurrentTime();
        
        messageDiv.appendChild(timeDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        scrollToBottom();
    }

    // Append a system message to the chat
    function appendSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-system';
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        scrollToBottom();
    }

    // Get current time in HH:MM format
    function getCurrentTime() {
        const now = new Date();
        return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Clear input and append user message
        messageInput.value = '';
        appendUserMessage(message);
    
        // If we already have a summary, we’re at the confirmation step.
        if (ticketSummary) {
            if (message.toLowerCase() === 'yes' || message.toLowerCase() === 'y') {
                // Confirm: create the ticket using the stored summary.
                createTicket(ticketSummary);
                startNewChat();
            } else if (message.toLowerCase() === 'no' || message.toLowerCase() === 'n') {
                // Reject: reset and restart the chat.
                ticketSummary = null;
                startNewChat();
            } else {
                // If the answer isn’t yes/no, prompt the user to confirm.
                appendSystemMessage("Please reply with 'yes' or 'no' to confirm the summary.");
            }
            return; // Exit here so we don't continue to send the message to /api/chat/respond.
        }
    
        // Normal chat flow: send message to the chat endpoint if no summary is pending.
        if (isChatActive) {
            fetch('/api/chat/respond', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                // Append the bot's response
                appendBotMessage(data.message);
                
                // If a summary is returned, store it for confirmation.
                if (data.summary) {
                    ticketSummary = data.summary;
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);
                appendSystemMessage('An error occurred. Please try again.');
            });
        } else if (currentTicketId) {
            // When replying to an existing ticket
            fetch(`/api/tickets/${currentTicketId}/reply`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // The message was sent successfully.
                }
            })
            .catch(error => {
                console.error('Error replying to ticket:', error);
                appendSystemMessage('An error occurred while sending your reply.');
            });
        }
    });
    

    // Create a new ticket with the summary
    function createTicket(summary) {
        fetch('/api/tickets/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ summary })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                appendSystemMessage(data.message);
                ticketSummary = null;
                isChatActive = false;
                // Refresh the ticket list
                loadTickets();
                startNewChat();
                // Load the newly created ticket
                setTimeout(() => {
                    loadTicket(data.ticket_id);
                }, 500);
            }
        })
        .catch(error => {
            console.error('Error creating ticket:', error);
            appendSystemMessage('An error occurred while creating your ticket.');
        });
    }

    // Load user's tickets
    function loadTickets() {
        fetch('/api/tickets')
            .then(response => response.json())
            .then(data => {
                // Clear existing ticket list
                ticketList.innerHTML = '';
                
                // Add each ticket to the list
                data.forEach(ticket => {
                    const ticketItem = document.createElement('li');
                    ticketItem.className = 'ticket-item';
                    ticketItem.dataset.id = ticket.id;
                    
                    const titleDiv = document.createElement('div');
                    titleDiv.className = 'ticket-title';
                    titleDiv.textContent = ticket.title;
                    
                    const metaDiv = document.createElement('div');
                    metaDiv.className = 'ticket-meta';
                    metaDiv.textContent = `#${ticket.id} · ${ticket.status} · ${ticket.created_at}`;
                    
                    ticketItem.appendChild(titleDiv);
                    ticketItem.appendChild(metaDiv);
                    
                    // Add click event to load ticket
                    ticketItem.addEventListener('click', function() {
                        loadTicket(ticket.id);
                    });
                    
                    ticketList.appendChild(ticketItem);
                });
                
                // If we have tickets, select the first one
                if (data.length > 0 && !currentTicketId) {
                    loadTicket(data[0].id);
                }
            })
            .catch(error => {
                console.error('Error loading tickets:', error);
                ticketList.innerHTML = '<li class="text-center">Error loading tickets</li>';
            });
    }

    // New Chat button click handler
    document.getElementById('new-chat-btn').addEventListener('click', function() {
        startNewChat();
        
        // Update the chat header
        document.getElementById('chat-title').textContent = 'New Conversation';
        
        // Deselect any active ticket
        document.querySelectorAll('.ticket-item').forEach(item => {
            item.classList.remove('active');
        });
        
        currentTicketId = null;
    });

    // Initially load tickets and start a new chat if no tickets
    loadTickets();
    startNewChat();
});
