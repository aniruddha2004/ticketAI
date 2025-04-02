import json
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, mongo
from models import User, Ticket, UserRole, TicketStatus
# from models import Message
from utils import generate_ticket_summary, get_category, get_priority, get_potential_cause
from datetime import datetime
# from bson.objectid import ObjectId

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_professional():
            return redirect(url_for('tickets'))
        else:
            return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.is_professional():
                    next_page = url_for('tickets')
                else:
                    next_page = url_for('chat')
            
            return redirect(next_page)
        
        flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.get_by_email(email):
        flash('Email already exists', 'error')
        return redirect(url_for('login'))
    
    # Generate username from email (part before @)
    username = email.split('@')[0]
    
    # Ensure username is unique
    base_username = username
    counter = 1
    while User.get_by_username(username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create and save the user
    user = User(username=username, email=email, role=UserRole.USER.value, category=None)
    user.set_password(password)
    user.save()
    
    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    # Get user's tickets for the sidebar
    user_tickets = Ticket.get_by_creator(current_user.id)
    return render_template('chat.html', user_tickets=user_tickets)

@app.route('/tickets')
@login_required
def tickets():
    if not current_user.is_professional():
        flash('Access denied', 'error')
        return redirect(url_for('chat'))
    
    # Get tickets for the assignee
    tickets = Ticket.get_by_assignee_id(current_user.id)
    
    return render_template('tickets.html', tickets=tickets)

@app.route('/api/tickets', methods=['GET'])
@login_required
def get_tickets():
    if current_user.is_professional():
        tickets = Ticket.get_by_assignee_id(current_user.id)
    else:
        tickets = Ticket.get_by_creator(current_user.id)
    
    # if not tickets :
    #     print(f"\n\n\n\n\n\n\nNo tickets foundn\n\n\n\n\n\n")
    
    # print(f"\n\n\n\n\n\n\n{tickets.id}\n\n\n\n\n\n")
    
    tickets_data = []
    for ticket in tickets:
        tickets_data.append({
            'id': ticket.id,
            'title': ticket.title,
            'status': ticket.status,
            'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M'),
            'category': ticket.category,
            'priority': ticket.priority
        })
    
    return jsonify(tickets_data)

@app.route('/api/tickets/<ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    if not current_user.is_professional() and ticket.creator_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    creator = User.get_by_id(ticket.creator_id)
    assignee = User.get_by_id(ticket.assignee_id) if ticket.assignee_id else None

    ticket_data = {
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'cause': ticket.cause,
        'status': ticket.status,
        'category': ticket.category,
        'priority': ticket.priority,
        'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M'),
        'creator': creator.username if creator else 'Unknown',
        'assignee': assignee.username if assignee else None,
    }

    return jsonify(ticket_data)


@app.route('/api/tickets/<ticket_id>/status', methods=['PUT'])
@login_required
def update_ticket_status(ticket_id):
    if not current_user.is_professional():
        return jsonify({'error': 'Access denied'}), 403
    
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    new_status = request.json.get('status')
    
    # Validate status
    if not new_status or new_status not in [status.value for status in TicketStatus]:
        return jsonify({'error': 'Invalid status'}), 400
    
    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()
    ticket.save()
    
    
    return jsonify({'success': True, 'status': new_status})

@app.route('/api/tickets/<ticket_id>/assign', methods=['PUT'])
@login_required
def assign_ticket(ticket_id):
    if not current_user.is_professional():
        return jsonify({'error': 'Access denied'}), 403
    
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    ticket.assignee_id = current_user.id
    
    # Update status if it's still open
    if ticket.status == TicketStatus.OPEN.value:
        ticket.status = TicketStatus.IN_PROGRESS.value
    
    ticket.save()

    
    return jsonify({'success': True})

@app.route('/api/chat/start', methods=['GET'])
@login_required
def start_chat():
    # Clear any existing chat session
    session.pop('chat_responses', None)
    session.pop('chat_step', None)
    
    session['chat_responses'] = {}
    session['chat_step'] = 0
    
    return jsonify({
        'message': 'Hello! Please mention your issue.',
        'step': 0
    })

@app.route('/api/chat/respond', methods=['POST'])
@login_required
def chat_respond():
    chat_step = session.get('chat_step', 0)
    chat_responses = session.get('chat_responses', {})
    
    user_response = request.json.get('message', '')
    chat_responses[f'step_{chat_step}'] = user_response
    
    questions = [
        "Hello! Could you please describe the issue you're experiencing with our app?",
        "What specific transaction or service were you using when you encountered the issue?",
        "When did you first notice this problem, and has it happened before?",
        "Did you see any error messages or unusual notifications? If so, please share the details, along with information about your device or network if possible."
    ]
    
    chat_step += 1
    session['chat_step'] = chat_step
    session['chat_responses'] = chat_responses
    
    if chat_step < len(questions):
        return jsonify({
            'message': questions[chat_step],
            'step': chat_step
        })
    else:
        # Generate ticket summary
        summary = generate_ticket_summary(chat_responses)
        return jsonify({
            'message': f"Thank you for providing the information. Here's a summary of your issue:\n\n{summary}\n\nIs this correct? (yes/no)",
            'step': chat_step,
            'summary': summary
        })

@app.route('/api/tickets/create', methods=['POST'])
@login_required
def create_ticket():
    summary = request.json.get('summary', '')
    
    # Create a ticket with the information gathered
    category = get_category(summary)
    priority = get_priority(summary, category)
    
    user_log_doc = mongo.db.Logs.find_one({"user_id": current_user.id})
    log_data = user_log_doc.get("logs", []) if user_log_doc else []
    cause = get_potential_cause(summary, category, json.dumps(log_data, indent=2))
    
    print(f"\n\n\n\n{log_data}\n\n\n\n")
    
    ticket = Ticket(
        title=summary.split('\n')[0] if '\n' in summary else summary[:100],
        description=summary,
        cause=cause,
        category=category,
        priority=priority,
        creator_id=current_user.id,
        status=TicketStatus.OPEN.value
    )
    
    print(f"\n\n\n\n{ticket.title}\n\n\n\n")
    ticket.save()
    
    # Clear the chat session
    session.pop('chat_responses', None)
    session.pop('chat_step', None)
    
    return jsonify({
        'success': True,
        'ticket_id': ticket.id,
        'message': f"Ticket #{ticket.id} has been created successfully."
    })

# @app.route('/api/tickets/<ticket_id>/reply', methods=['POST'])
# @login_required
# def reply_to_ticket(ticket_id):
#     ticket = Ticket.get_by_id(ticket_id)
#     if not ticket:
#         return jsonify({'error': 'Ticket not found'}), 404
    
#     # Check permissions
#     if not current_user.is_professional() and ticket.creator_id != current_user.id:
#         return jsonify({'error': 'Access denied'}), 403
    
#     content = request.json.get('message', '')
    
#     if not content.strip():
#         return jsonify({'error': 'Message cannot be empty'}), 400
    
#     message = Message(
#         content=content,
#         ticket_id=ticket.id,
#         user_id=current_user.id
#     )
#     message.save()
    
#     return jsonify({
#         'success': True,
#         'message_id': message.id,
#         'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
#     })
