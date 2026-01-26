# Founding Families System

## Overview
The first 200 families who sign up get locked at £9.99/month for life, while regular members pay £14.99/month.

## How It Works

### 1. Interest Form Signup
- Users fill out the founding families form at `/founding/`
- Each signup is stored in the `FoundingFamilySignup` model
- Counter shows live progress: "X of 200 spots claimed"
- Form automatically closes when 200 signups are reached

### 2. Counter Display
The counter shows different messaging based on spots remaining:
- **More than 50 spots left**: Social proof messaging ("X families have already joined")
- **20-50 spots left**: Urgency messaging ("Hurry! Only X spots remaining")
- **Less than 20 spots left**: Scarcity messaging ("LAST CHANCE! Only X spots left")

### 3. Reserved Spots
- Total limit: 200 families
- Public limit: 190 families (shown on counter)
- Reserved: 10 spots (for VIPs, troubleshooting, etc.)
- To adjust, edit `FOUNDING_LIMIT` and `RESERVED_SPOTS` in `apps/founding/views.py`

### 4. Subscription Pricing
When a user starts their subscription:
1. System checks if their email exists in `FoundingFamilySignup` table
2. If found → £9.99/month, `founding_member=True`
3. If not found → £14.99/month, `founding_member=False`
4. The `founding_member` field is set on the `Subscription` model and never changes

### 5. Dashboard Display
Founding family members see a special badge on their dashboard:
- **✨ FOUNDING FAMILY MEMBER ✨**
- "£9.99/month locked for life"
- Reminder that regular members pay £14.99

## Technical Details

### Models
**FoundingFamilySignup** (`apps/founding/models.py`)
- email
- full_name
- created_at

**Subscription** (`apps/users/models.py`)
- founding_member (BooleanField, default=False)
- Locked price is enforced in Stripe checkout

### Views
**FoundingFamilySignupView** (`apps/founding/views.py`)
- Checks if limit reached before accepting signup
- Provides counter data to template

**create_checkout_session** (`apps/users/views.py`)
- Queries `FoundingFamilySignup` for user's email
- Sets price: 999 pence (£9.99) or 1499 pence (£14.99)
- Sets `founding_member` field on subscription

### Templates
**founding.html** (`apps/founding/templates/founding/founding.html`)
- Live counter with progress bar
- Dynamic messaging based on spots remaining
- Form disables when signups closed

**dashboard.html** (`apps/users/templates/users/dashboard.html`)
- Shows founding member badge if `founding_member=True`
- Displays locked price

## Admin Management

### View Current Signups
```bash
python manage.py shell -c "from apps.founding.models import FoundingFamilySignup; print(f'Total: {FoundingFamilySignup.objects.count()}'); [print(f'{s.email}') for s in FoundingFamilySignup.objects.all()]"
```

### Manually Add Founding Member
```python
from apps.founding.models import FoundingFamilySignup
FoundingFamilySignup.objects.create(
    email='special@example.com',
    full_name='VIP Customer'
)
```

### Check if User is Founding Member
```python
from apps.users.models import Subscription
sub = Subscription.objects.get(parent_profile__user__email='user@example.com')
print(f"Founding member: {sub.founding_member}")
```

### Manually Set User as Founding Member
```python
from apps.users.models import Subscription
sub = Subscription.objects.get(parent_profile__user__email='user@example.com')
sub.founding_member = True
sub.save()
```

## Testing

1. **Test the counter**: Visit `/founding/` to see live counter
2. **Test signup**: Fill out form and check database
3. **Test pricing**: Start subscription and check Stripe checkout price
4. **Test dashboard**: Login and verify founding member badge appears
5. **Test limit**: Create 200 test signups and verify form closes

## Future Enhancements
- Admin dashboard to view all founding families
- Email notifications when spots are running low
- Ability to export founding families list
- Analytics dashboard showing signup trends
