# Legal Ease Platform - Notification System Implementation

## Overview
This implementation adds a comprehensive notification system to the Legal Ease platform that sends welcome emails after user signup and verification using Kafka for event-driven communication.

## Architecture

### Services Involved
1. **Auth Service** - Handles user authentication and publishes events
2. **Notification Service** - Consumes events and sends notifications

### Event Flow
1. User signs up → Auth service publishes `user_signed_up` event
2. User verifies email → Auth service publishes `user_verified` event  
3. Notification service consumes events → Sends appropriate emails

## Implementation Details

### Auth Service Changes

#### Models Enhanced
- Added user types: PETITIONER, RESPONDENT, PROSECUTION, DEFENSE, MEDIATOR, JUDGE, COURT_STAFF, OBSERVER
- Added professional credentials fields (bar_number, license_number, organization)
- Added verification tracking fields

#### API Endpoints
- **POST /api/accounts/signup/** - Creates user and publishes signup event
- **POST /api/accounts/login/** - Authenticates user and publishes login event
- **POST /api/accounts/verify-email/** - Verifies email and publishes verification event
- **GET/PUT /api/accounts/profile/** - Manages user profile

#### Kafka Integration
- Enabled Kafka producer in `kafka_producer.py`
- Publishing JSON-formatted events with comprehensive user data
- Events: `user_signed_up`, `user_logged_in`, `user_verified`

### Notification Service Implementation

#### Models Created
- **NotificationType** - Defines types of notifications (EMAIL, SMS, PUSH, IN_APP)
- **NotificationTemplate** - Stores email templates with variables
- **Notification** - Tracks individual notification records
- **NotificationPreference** - User notification preferences

#### Core Components

##### EmailService (`utils.py`)
- Handles SMTP email sending
- Supports both Django email backend and direct SMTP
- HTML and plain text email support
- Attachment support

##### NotificationService (`utils.py`)
- Main service for handling notifications
- `send_welcome_notification()` - Sends welcome emails
- `send_verification_notification()` - Sends verification emails
- Template rendering with Django template engine
- Preference checking

##### KafkaConsumer (`kafka_consumer.py`)
- Consumes events from multiple topics
- Routes messages to appropriate handlers
- Error handling and logging
- Supports both JSON and simple comma-separated formats

#### Email Templates
Created default templates for:
- **Welcome Email** - Sent after successful signup verification
- **Email Verification** - Sent during signup process

Templates support variables:
- `{{username}}` - User's display name
- `{{user_type}}` - Type of user (Petitioner, Judge, etc.)
- `{{platform_name}}` - Platform name
- `{{login_url}}` - URL to login page
- `{{support_email}}` - Support email address
- `{{verification_url}}` - Email verification URL

#### Management Command
- **`python manage.py consume_notifications`** - Starts Kafka consumer
- Optional `--topics` parameter to specify specific topics

## Configuration

### Auth Service Settings
```python
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
```

### Notification Service Settings
```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Kafka Configuration  
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_CONSUMER_GROUP = 'notification_service'

# Platform URLs
FRONTEND_BASE_URL = 'http://localhost:3000'
FRONTEND_LOGIN_URL = 'http://localhost:3000/login'
SUPPORT_EMAIL = 'support@legalease.com'
```

## Setup Instructions

### 1. Install Dependencies
```bash
# Auth Service
cd services/auth_service
pip install confluent-kafka

# Notification Service  
cd services/notification_service
pip install -r requirements.txt
```

### 2. Database Migration
```bash
# Auth Service
cd services/auth_service
python manage.py makemigrations
python manage.py migrate

# Notification Service
cd services/notification_service  
python manage.py makemigrations
python manage.py migrate
```

### 3. Start Kafka (if not running)
```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

### 4. Run Services
```bash
# Terminal 1: Auth Service
cd services/auth_service
python manage.py runserver 8000

# Terminal 2: Notification Service
cd services/notification_service
python manage.py runserver 8001

# Terminal 3: Kafka Consumer
cd services/notification_service
python manage.py consume_notifications
```

## Usage Flow

### User Signup and Welcome Email
1. **User Signs Up**
   ```bash
   POST /api/accounts/signup/
   {
     "username": "john_doe",
     "email": "john@example.com", 
     "password": "securepass123",
     "user_type": "PETITIONER",
     "first_name": "John",
     "last_name": "Doe"
   }
   ```

2. **Auth Service Response**
   ```json
   {
     "message": "User created successfully. Welcome email will be sent shortly.",
     "user": { /* user data */ }
   }
   ```

3. **Kafka Event Published**
   ```json
   {
     "user_id": "123e4567-e89b-12d3-a456-426614174000",
     "email": "john@example.com",
     "username": "john_doe", 
     "user_type": "PETITIONER",
     "is_verified": false,
     "created_at": "2025-09-20T17:30:00Z"
   }
   ```

4. **Welcome Email Sent** - User receives welcome email with platform information

### Email Verification
1. **User Verifies Email**
   ```bash
   POST /api/accounts/verify-email/
   {
     "user_id": "123e4567-e89b-12d3-a456-426614174000",
     "token": "verification-token-here"
   }
   ```

2. **Verification Event Published** - Triggers any post-verification notifications

## Features

### Email Features
- **Professional Templates** - Branded HTML emails with fallback text
- **Template Variables** - Dynamic content based on user data
- **Preference Management** - Users can control notification types
- **Delivery Tracking** - Track sent, delivered, failed status
- **Retry Logic** - Automatic retry for failed notifications
- **Attachment Support** - Can include documents in emails

### Kafka Features  
- **Event-Driven Architecture** - Decoupled services communication
- **Multiple Event Types** - Support for various platform events
- **Error Handling** - Robust error handling and logging
- **Scalable** - Can handle high message volumes
- **Consumer Groups** - Multiple consumers for load balancing

### User Management Features
- **Legal User Types** - Specific roles for court proceedings
- **Professional Credentials** - Bar numbers, licenses, organizations
- **Verification System** - Email verification workflow
- **Profile Management** - Comprehensive user profiles

## Security Considerations

1. **Email Templates** - XSS protection through Django template escaping
2. **Kafka Security** - Consider enabling SASL/SSL for production
3. **Email Credentials** - Use app passwords or OAuth for Gmail
4. **User Data** - Minimal PII in Kafka messages
5. **Verification Tokens** - Implement proper token validation

## Monitoring and Logging

- **Django Logging** - Comprehensive logging configuration
- **Kafka Consumer Logs** - Message processing tracking  
- **Email Delivery Logs** - Success/failure tracking
- **Database Records** - All notifications stored for audit

## Future Enhancements

1. **SMS Notifications** - Add SMS support using Twilio/AWS SNS
2. **Push Notifications** - Mobile app push notifications
3. **Template Editor** - Admin interface for template management
4. **Advanced Scheduling** - Delayed and recurring notifications
5. **Analytics** - Notification delivery and engagement metrics
6. **A/B Testing** - Template variation testing
7. **Webhook Support** - External system integrations

This implementation provides a solid foundation for a comprehensive notification system that can scale with the Legal Ease platform's growth.
