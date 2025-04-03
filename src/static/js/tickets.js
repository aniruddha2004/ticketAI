document.addEventListener('DOMContentLoaded', function() {
    const ticketsTable = document.getElementById('tickets-table');
    const ticketsTableBody = document.getElementById('tickets-table-body');
    const ticketModal = document.getElementById('ticket-modal');
    const ticketModalTitle = document.getElementById('ticket-modal-title');
    const ticketModalContent = document.getElementById('ticket-modal-content');
    const ticketModalMessages = document.getElementById('ticket-modal-messages');
    const ticketModalForm = document.getElementById('ticket-modal-form');
    const ticketModalClose = document.getElementById('ticket-modal-close');
    const statusFilter = document.getElementById('status-filter');
    
    let currentTicketId = null;
    
    // Load all tickets for the professional
    function loadTickets() {
        // Get selected status filter
        const statusValue = statusFilter ? statusFilter.value : '';
        
        fetch('/api/tickets')
            .then(response => response.json())
            .then(data => {
                if(!data) {
                    console.log("No data!")
                }
                console.log(data)
                // Clear existing table rows
                ticketsTableBody.innerHTML = '';
                
                // Filter tickets if status filter is set
                const filteredTickets = statusValue ? 
                    data.filter(ticket => ticket.status === statusValue) : 
                    data;
                
                // Add each ticket to the table
                filteredTickets.forEach(ticket => {
                    const row = document.createElement('tr');
                    row.dataset.id = ticket.id;
                    
                    // Ticket ID
                    const idCell = document.createElement('td');
                    idCell.textContent = `#${ticket.id}`;
                    
                    // Ticket Title
                    const titleCell = document.createElement('td');
                    const titleLink = document.createElement('a');
                    titleLink.href = '#';
                    titleLink.textContent = ticket.title;
                    titleLink.addEventListener('click', function(e) {
                        e.preventDefault();
                        openTicketModal(ticket.id);
                    });
                    titleCell.appendChild(titleLink);
                    
                    // Category
                    const categoryCell = document.createElement('td');
                    categoryCell.textContent = ticket.category || 'General';
                    
                    // Created Date
                    const dateCell = document.createElement('td');
                    dateCell.textContent = ticket.created_at;
                    
                    // Status
                    const statusCell = document.createElement('td');
                    const statusBadge = document.createElement('span');
                    statusBadge.className = `badge badge-${ticket.status}`;
                    statusBadge.textContent = ticket.status;
                    statusCell.appendChild(statusBadge);
                    
                    // Priority
                    const priorityCell = document.createElement('td');
                    if (ticket.priority) {
                        const priorityBadge = document.createElement('span');
                        priorityBadge.className = `badge badge-${ticket.priority.toLowerCase()}`;
                        priorityBadge.textContent = ticket.priority;
                        priorityCell.appendChild(priorityBadge);
                    } else {
                        priorityCell.textContent = 'Medium';
                    }
                    
                    // Actions
                    const actionsCell = document.createElement('td');
                    
                    const viewBtn = document.createElement('button');
                    viewBtn.className = 'btn btn-sm btn-primary';
                    viewBtn.textContent = 'View';
                    viewBtn.addEventListener('click', function() {
                        openTicketModal(ticket.id);
                    });
                    
                    actionsCell.appendChild(viewBtn);
                    
                    // Add all cells to the row
                    row.appendChild(idCell);
                    row.appendChild(titleCell);
                    row.appendChild(categoryCell);
                    row.appendChild(dateCell);
                    row.appendChild(statusCell);
                    row.appendChild(priorityCell);
                    row.appendChild(actionsCell);
                    
                    // Add row to table body
                    ticketsTableBody.appendChild(row);
                });
                
                // Show message if no tickets
                if (filteredTickets.length === 0) {
                    const emptyRow = document.createElement('tr');
                    const emptyCell = document.createElement('td');
                    emptyCell.colSpan = 7;
                    emptyCell.textContent = 'No tickets found.';
                    emptyCell.className = 'text-center';
                    emptyRow.appendChild(emptyCell);
                    ticketsTableBody.appendChild(emptyRow);
                }
            })
            .catch(error => {
                console.error('Error loading tickets:', error);
                ticketsTableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center">Error loading tickets. Please try again.</td>
                    </tr>
                `;
            });
    }
    
    // Open ticket modal with details
    function openTicketModal(ticketId) {
        currentTicketId = ticketId;
        
        // Clear previous content
        ticketModalTitle.textContent = 'Loading...';
        ticketModalContent.innerHTML = '';
        // ticketModalMessages.innerHTML = '';
        
        // Show modal
        ticketModal.style.display = 'block';
        
        // Load ticket details
        fetch(`/api/tickets/${ticketId}`)
            .then(response => response.json())
            .then(data => {
                console.log(data.id)
                // Update modal title
                ticketModalTitle.textContent = `Ticket #${data.id}: ${data.title}`;
                
                // Create ticket details
                const detailsHTML = `
                    <div class="ticket-details">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Status:</strong> <span class="badge badge-${data.status}">${data.status}</span></p>
                                <p><strong>Category:</strong> ${data.category || 'General'}</p>
                                <p><strong>Priority:</strong> ${data.priority || 'Medium'}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Created By:</strong> ${data.creator}</p>
                                <p><strong>Created At:</strong> ${data.created_at}</p>
                                <p><strong>Assigned To:</strong> ${data.assignee || 'Unassigned'}</p>
                            </div>
                        </div>
                        
                        <div class="ticket-description mt-3">
                            <h5>Description:</h5>
                            <p>${data.description}</p>
                            <h5>Potential Cause:</h5>
                            <p>${data.cause}</p>
                        </div>
                        
                        <div class="ticket-actions mt-3">
                            <div class="status-dropdown d-inline-block">
                                <select id="status-select" class="form-control form-control-sm d-inline-block custom-select" style="width: auto; color: white;">
                                    <option value="open" ${data.status === 'open' ? 'selected' : ''}>Open</option>
                                    <option value="in_progress" ${data.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                    <option value="resolved" ${data.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                                    <option value="closed" ${data.status === 'closed' ? 'selected' : ''}>Closed</option>
                                </select>
                                <button id="update-status-btn" class="btn btn-secondary">Update Status</button>
                            </div>
                        </div>
                    </div>
                `;
                
                ticketModalContent.innerHTML = detailsHTML;
                
                // // Add messages to conversation
                // ticketModalMessages.innerHTML = '<h5>Conversation:</h5>';
                
                // data.messages.forEach(message => {
                //     const messageDiv = document.createElement('div');
                //     messageDiv.className = 'ticket-message';
                    
                //     if (message.is_system) {
                //         messageDiv.className += ' ticket-message-system';
                //         messageDiv.innerHTML = `<div class="message-content">${message.content}</div>
                //                                <div class="message-meta">${message.created_at}</div>`;
                //     } else {
                //         messageDiv.className += ' ticket-message-user';
                //         messageDiv.innerHTML = `<div class="message-header">
                //                                  <strong>${message.username}</strong>
                //                                  <span class="message-time">${message.created_at}</span>
                //                                </div>
                //                                <div class="message-content">${message.content}</div>`;
                //     }
                    
                //     ticketModalMessages.appendChild(messageDiv);
                // });
                
                // Setup action buttons
                document.getElementById('update-status-btn').addEventListener('click', function() {
                    updateTicketStatus(ticketId, document.getElementById('status-select').value);
                });
                
                // document.getElementById('assign-btn').addEventListener('click', function() {
                //     assignTicket(ticketId);
                // });
            })
            .catch(error => {
                console.error('Error loading ticket details:', error);
                ticketModalContent.innerHTML = '<div class="alert alert-danger">Error loading ticket details. Please try again.</div>';
            });
    }
    
    // Update ticket status
    function updateTicketStatus(ticketId, status) {
        fetch(`/api/tickets/${ticketId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                const successDiv = document.createElement('div');
                successDiv.className = 'alert alert-success mt-3';
                successDiv.textContent = `Status updated to "${status}"`;
                ticketModalContent.appendChild(successDiv);
                
                // Update ticket in the table
                loadTickets();
                
                // Reload ticket details after a short delay
                setTimeout(() => {
                    openTicketModal(ticketId);
                }, 1500);
            }
        })
        .catch(error => {
            console.error('Error updating ticket status:', error);
            
            // Show error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-3';
            errorDiv.textContent = 'Error updating ticket status. Please try again.';
            ticketModalContent.appendChild(errorDiv);
        });
    }
    
    // Assign ticket to self
    function assignTicket(ticketId) {
        fetch(`/api/tickets/${ticketId}/assign`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                const successDiv = document.createElement('div');
                successDiv.className = 'alert alert-success mt-3';
                successDiv.textContent = 'Ticket assigned to you successfully';
                ticketModalContent.appendChild(successDiv);
                
                // Update ticket in the table
                loadTickets();
                
                // Reload ticket details after a short delay
                setTimeout(() => {
                    openTicketModal(ticketId);
                }, 1500);
            }
        })
        .catch(error => {
            console.error('Error assigning ticket:', error);
            
            // Show error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-3';
            errorDiv.textContent = 'Error assigning ticket. Please try again.';
            ticketModalContent.appendChild(errorDiv);
        });
    }
    
    // Close modal when clicking the close button
    ticketModalClose.addEventListener('click', function() {
        ticketModal.style.display = 'none';
    });
    
    // Close modal when clicking outside the modal content
    window.addEventListener('click', function(event) {
        if (event.target === ticketModal) {
            ticketModal.style.display = 'none';
        }
    });
    
    // Handle form submission for replying to ticket
    // ticketModalForm.addEventListener('submit', function(e) {
    //     e.preventDefault();
        
    //     const messageInput = document.getElementById('ticket-reply-input');
    //     const message = messageInput.value.trim();
        
    //     if (!message || !currentTicketId) return;
        
    //     // Clear input
    //     messageInput.value = '';
        
    //     // Send reply
    //     fetch(`/api/tickets/${currentTicketId}/reply`, {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify({ message })
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.success) {
    //             // Reload ticket to show new message
    //             openTicketModal(currentTicketId);
    //         }
    //     })
    //     .catch(error => {
    //         console.error('Error sending reply:', error);
            
    //         // Show error message
    //         const errorDiv = document.createElement('div');
    //         errorDiv.className = 'alert alert-danger mt-2';
    //         errorDiv.textContent = 'Error sending reply. Please try again.';
    //         ticketModalForm.appendChild(errorDiv);
            
    //         // Remove error message after 3 seconds
    //         setTimeout(() => {
    //             ticketModalForm.removeChild(errorDiv);
    //         }, 3000);
    //     });
    // });
    
    // Handle status filter change
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            loadTickets();
        });
    }
    
    // Initial load of tickets
    loadTickets();
});
