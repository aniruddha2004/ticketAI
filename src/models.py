from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from bson.objectid import ObjectId

class UserRole(Enum):
    USER = 'user'
    PROFESSIONAL = 'professional'

class TicketStatus(Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'

class User(UserMixin):
    def __init__(self, username, email, password_hash=None, role=UserRole.USER.value, category=None, _id=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.category = category
        self._id = _id  # Store the provided _id, or None if not provided

    @property
    def id(self):
        return str(self._id) if self._id is not None else None
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_professional(self):
        return self.role == UserRole.PROFESSIONAL.value
    
    @staticmethod
    def get_by_id(user_id):
        from app import mongo
        user_data = mongo.db.Users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                category=user_data.get('category'),
                _id=user_data.get('_id')
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        from app import mongo
        user_data = mongo.db.Users.find_one({"email": email})
        if user_data:
            return User(
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                category=user_data.get('category'),
                _id=user_data.get('_id')
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        from app import mongo
        user_data = mongo.db.Users.find_one({"username": username})
        if user_data:
            return User(
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                category=user_data.get('category'),
                _id=user_data.get('_id')
            )
        return None
    
    def save(self):
        from app import mongo
        if not self.password_hash:
            raise ValueError("User must have a password")
        
        user_data = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "category": self.category
        }
        
        print("\n\n\n\nSave Functionn\n\n\n\n")
        
        if hasattr(self, '_id') and self._id:
            mongo.db.Users.update_one({"_id": self._id}, {"$set": user_data})
        else:
            result = mongo.db.Users.insert_one(user_data)
            self._id = result.inserted_id
            print("\n\n\n\n\n\nInserted user with _id:", self._id)  # Temporary debugging line
        
        return self

class Ticket:
    def __init__(self, title, description, cause, creator_id, category=None, priority=None, 
                 status=TicketStatus.OPEN.value, assignee_id=None, created_at=None, 
                 updated_at=None, _id=None, ):
        self.title = title
        self.description = description
        self.cause = cause
        self.category = category
        self.status = status
        self.priority = priority
        self.creator_id = creator_id
        self.assignee_id = assignee_id
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()
        self._id = _id  # Store the provided _id, or None if not provided

    @property
    def id(self):
        return str(self._id) if self._id is not None else None
    
    @staticmethod
    def get_by_id(ticket_id):
        from app import mongo
        ticket_data = mongo.db.Tickets.find_one({"_id": ObjectId(ticket_id)})
        if ticket_data:
            return Ticket(
                title=ticket_data.get('title'),
                description=ticket_data.get('description'),
                cause=ticket_data.get('cause'),
                category=ticket_data.get('category'),
                status=ticket_data.get('status'),
                priority=ticket_data.get('priority'),
                creator_id=ticket_data.get('creator_id'),
                assignee_id=ticket_data.get('assignee_id'),
                created_at=ticket_data.get('created_at'),
                updated_at=ticket_data.get('updated_at'),
                _id=ticket_data.get('_id')
            )
        return None
    
    @staticmethod
    def get_by_assignee_id(assignee_id):
        from app import mongo
        print(f"\n\n\n\n\n\n\n{assignee_id}\n\n\n\n\n\n")
        tickets = []
        for ticket_data in mongo.db.Tickets.find({"assignee_id": assignee_id}):
            tickets.append(Ticket(
                title=ticket_data.get('title'),
                description=ticket_data.get('description'),
                cause=ticket_data.get('cause'),
                category=ticket_data.get('category'),
                status=ticket_data.get('status'),
                priority=ticket_data.get('priority'),
                creator_id=ticket_data.get('creator_id'),
                assignee_id=ticket_data.get('assignee_id'),
                created_at=ticket_data.get('created_at'),
                updated_at=ticket_data.get('updated_at'),
                _id=ticket_data.get('_id')
            ))
        return tickets
    
    @staticmethod
    def get_by_creator(creator_id):
        from app import mongo
        tickets = []
        for ticket_data in mongo.db.Tickets.find({"creator_id": creator_id}).sort("created_at", -1):
            tickets.append(Ticket(
                title=ticket_data.get('title'),
                description=ticket_data.get('description'),
                cause=ticket_data.get('cause'),
                category=ticket_data.get('category'),
                status=ticket_data.get('status'),
                priority=ticket_data.get('priority'),
                creator_id=ticket_data.get('creator_id'),
                assignee_id=ticket_data.get('assignee_id'),
                created_at=ticket_data.get('created_at'),
                updated_at=ticket_data.get('updated_at'),
                _id=ticket_data.get('_id')
            ))
        return tickets
    
    @staticmethod
    def get_by_category(category):
        from app import mongo
        tickets = []
        for ticket_data in mongo.db.Tickets.find({"category": category}).sort("created_at", -1):
            tickets.append(Ticket(
                title=ticket_data.get('title'),
                description=ticket_data.get('description'),
                cause=ticket_data.get('cause'),
                category=ticket_data.get('category'),
                status=ticket_data.get('status'),
                priority=ticket_data.get('priority'),
                creator_id=ticket_data.get('creator_id'),
                assignee_id=ticket_data.get('assignee_id'),
                created_at=ticket_data.get('created_at'),
                updated_at=ticket_data.get('updated_at'),
                _id=ticket_data.get('_id')
            ))
        return tickets
    
    @staticmethod
    def get_all():
        from app import mongo
        tickets = []
        for ticket_data in mongo.db.Tickets.find().sort("created_at", -1):
            tickets.append(Ticket(
                title=ticket_data.get('title'),
                description=ticket_data.get('description'),
                cause=ticket_data.get('cause'),
                category=ticket_data.get('category'),
                status=ticket_data.get('status'),
                priority=ticket_data.get('priority'),
                creator_id=ticket_data.get('creator_id'),
                assignee_id=ticket_data.get('assignee_id'),
                created_at=ticket_data.get('created_at'),
                updated_at=ticket_data.get('updated_at'),
                _id=ticket_data.get('_id')
            ))
        return tickets
    
    def save(self):
        from app import mongo
        ticket_data = {
            "title": self.title,
            "description": self.description,
            "cause": self.cause,
            "category": self.category,
            "status": self.status,
            "priority": self.priority,
            "creator_id": self.creator_id,
            "assignee_id": self.assignee_id,
            "created_at": self.created_at,
            "updated_at": datetime.utcnow()
        }
        
        if hasattr(self, '_id') and self._id:
            mongo.db.Tickets.update_one({"_id": self._id}, {"$set": ticket_data})
        else:
            result = mongo.db.Tickets.insert_one(ticket_data)
            self._id = result.inserted_id
        
        return self

# class Message:
#     def __init__(self, content, ticket_id, user_id=None, is_system=False, created_at=None, _id=None):
#         self.content = content
#         self.ticket_id = ticket_id
#         self.user_id = user_id
#         self.is_system = is_system
#         self.created_at = created_at if created_at else datetime.utcnow()
#         # self._id = _id if _id else ObjectId()
    
#     @property
#     def id(self):
#         return str(self._id)
    
#     @staticmethod
#     def get_by_ticket(ticket_id):
#         from app import mongo
#         messages = []
#         for message_data in mongo.db.Messages.find({"ticket_id": ticket_id}).sort("created_at", 1):
#             messages.append(Message(
#                 content=message_data.get('content'),
#                 ticket_id=message_data.get('ticket_id'),
#                 user_id=message_data.get('user_id'),
#                 is_system=message_data.get('is_system'),
#                 created_at=message_data.get('created_at'),
#                 _id=message_data.get('_id')
#             ))
#         return messages
    
#     def save(self):
#         from app import mongo
#         message_data = {
#             "content": self.content,
#             "ticket_id": self.ticket_id,
#             "user_id": self.user_id,
#             "is_system": self.is_system,
#             "created_at": self.created_at
#         }
        
#         if hasattr(self, '_id') and self._id:
#             mongo.db.Messages.update_one({"_id": self._id}, {"$set": message_data})
#         else:
#             result = mongo.db.Messages.insert_one(message_data)
#             self._id = result.inserted_id
        
#         return self
