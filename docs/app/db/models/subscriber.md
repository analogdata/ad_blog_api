# Subscriber Model Documentation

The `Subscriber` model manages email newsletter subscriptions in the blog API, handling subscription status, verification, and lifecycle management.

## Model Overview

The `Subscriber` model implements timestamp fields directly with database-driven defaults. It manages email subscribers, including their verification status and subscription lifecycle.

## Fields and Properties

| Field | Type | Description | Indexes |
|-------|------|-------------|---------|
| `id` | int | Primary key | Primary key |
| `email` | EmailStr | Subscriber's email address | Unique, Indexed |
| `is_active` | bool | Whether the subscription is active | - |
| `is_verified` | bool | Whether the email has been verified | - |
| `verification_token` | Optional[str] | Token for email verification | - |
| `subscribed_at` | datetime | When the subscription was created | - |
| `verified_at` | Optional[datetime] | When the email was verified | - |
| `unsubscribed_at` | Optional[datetime] | When the subscription was canceled | - |
| `created_at` | datetime | When the record was created (database-driven) | - |
| `updated_at` | datetime | When the record was last updated (database-driven) | - |

## Methods

### Verification and Subscription Management

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `validate_subscriber()` | None | Subscriber | Validates subscriber data and generates verification token if needed |
| `generate_verification_token()` (classmethod) | None | str | Generates a secure random verification token |
| `verify()` | None | None | Marks the subscriber as verified |
| `unsubscribe()` | None | None | Marks the subscriber as unsubscribed |
| `resubscribe()` | None | None | Reactivates a previously unsubscribed subscriber |

## Usage Flow

### Subscription Creation

```python
# Create a new subscriber (verification token is auto-generated)
subscriber = Subscriber(email="user@example.com")
db.add(subscriber)
db.commit()
```

### Email Verification Process

```python
# Send verification email (application logic)
send_verification_email(subscriber.email, subscriber.verification_token)

# When user clicks verification link
subscriber = db.query(Subscriber).filter(
    Subscriber.verification_token == token
).first()

if subscriber:
    subscriber.verify()
    db.add(subscriber)
    db.commit()
```

### Unsubscribe and Resubscribe

```python
# Unsubscribe
subscriber = db.query(Subscriber).filter(Subscriber.email == email).first()
subscriber.unsubscribe()
db.add(subscriber)
db.commit()

# Resubscribe
subscriber.resubscribe()
db.add(subscriber)
db.commit()
```

### Querying Subscribers

```python
# Get all active and verified subscribers
active_subscribers = db.query(Subscriber).filter(
    Subscriber.is_active == True,
    Subscriber.is_verified == True
).all()

# Get recently subscribed users
from datetime import datetime, timedelta, timezone
recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
recent_subscribers = db.query(Subscriber).filter(
    Subscriber.subscribed_at >= recent_cutoff
).all()
```

## Design Considerations

1. **Email Validation**: The model uses Pydantic's `EmailStr` type to ensure valid email formats.

2. **Verification Flow**: The model implements a double opt-in process:
   - User subscribes (is_active=True, is_verified=False)
   - Verification email is sent with a token
   - User verifies email (is_verified=True)
   - Only verified subscribers receive communications

3. **Soft Unsubscribe**: Rather than deleting records when users unsubscribe, the model uses a soft unsubscribe approach (is_active=False), which:
   - Preserves subscription history
   - Allows for resubscription
   - Prevents sending emails to unsubscribed users
   - Complies with privacy regulations by maintaining unsubscribe records

4. **Secure Tokens**: Verification tokens are generated using `secrets.token_urlsafe()`, which provides cryptographically strong random tokens suitable for email verification.

## Database Impact

- The unique index on `email` ensures each email can only have one subscription record and optimizes lookups by email address.
- Timestamp fields enable analytics on subscription patterns and retention.

## Subscription Lifecycle

The subscriber model supports the following lifecycle states:

1. **Pending Verification**:
   - `is_active = True`
   - `is_verified = False`
   - `verification_token` is set
   - User has subscribed but not confirmed their email

2. **Active Subscription**:
   - `is_active = True`
   - `is_verified = True`
   - `verification_token = None`
   - User has confirmed their email and receives communications

3. **Unsubscribed**:
   - `is_active = False`
   - `is_verified` remains unchanged
   - `unsubscribed_at` is set
   - User has opted out of communications

## Email Campaign Integration

While not directly part of the model, the `Subscriber` model is designed to integrate with email campaign systems:

```python
# Example: Get subscribers for a newsletter campaign
subscribers_for_campaign = db.query(Subscriber).filter(
    Subscriber.is_active == True,
    Subscriber.is_verified == True
).all()

# Extract emails for campaign
subscriber_emails = [sub.email for sub in subscribers_for_campaign]
```

This allows for easy integration with email service providers or internal email sending systems.
