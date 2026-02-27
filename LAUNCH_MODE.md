# Launch Mode Configuration

Zonuko has two launch modes to control the signup flow and public navigation.

## Modes

### FOUNDING Mode (Default)
- **Purpose**: Pre-launch mode to collect up to 200 founding family signups
- **Features**:
  - Home page CTA: "Claim Your Spot (X left)" → Founding form
  - Auto-switches to "Join Waitlist" when 200 signups reached
  - Founding pricing: £9.99/month (locked forever)
  - Public nav shows "Claim Your Spot" button
  - No Login/Signup links in public nav (founding form only)

### PUBLIC Mode
- **Purpose**: Post-launch mode with open public signup
- **Features**:
  - Home page CTA: "Start Free Trial" → Regular signup
  - Shows "Already a member? Log in" link
  - Public pricing: £14.99/month
  - Founding members still get £9.99/month (detected by email)
  - Public nav shows "Log in" and "Start Free Trial" buttons

## How to Change Mode

### Development (Local)
Set environment variable in your terminal or `.env` file:
```bash
LAUNCH_MODE=PUBLIC
```

Or keep default:
```bash
LAUNCH_MODE=FOUNDING
```

### Production (Deployment)
1. Set environment variable in your hosting platform (e.g., Railway, Heroku)
2. Restart the server for changes to take effect
3. Verify home page shows correct CTA

## Launch Checklist

### Before Going Public (FOUNDING → PUBLIC)
- [ ] Verify you have ~200 founding signups (check founding dashboard)
- [ ] Test email server is configured (password resets, verifications)
- [ ] Ensure Stripe webhooks are set up for subscriptions
- [ ] Test public signup flow end-to-end (trial → add child → start project)
- [ ] Verify founding members still get £9.99 pricing

### Switching to PUBLIC Mode
1. Set `LAUNCH_MODE=PUBLIC` in production environment variables
2. Restart the server
3. Check home page shows "Start Free Trial" CTA
4. Verify public nav shows "Log in" link
5. Test signup flow creates new accounts correctly
6. Monitor that founding members still get founding pricing

## Technical Details

- **Setting Location**: `zonuko/settings.py` line ~30
- **Context Processor**: `zonuko/context_processors.py` makes `launch_mode` available in all templates
- **Home Page Logic**: `apps/core/templates/core/home.html` shows different CTAs based on mode
- **Navigation Logic**: `templates/partials/nav.html` shows different buttons based on mode
- **Founding Cap**: Enforced in `apps/founding/views.py` (FOUNDING_LIMIT = 200)

## Founding Member Detection

Founding pricing (£9.99/month) is detected by checking if user's email exists in `FoundingFamilySignup` table. This works in both FOUNDING and PUBLIC modes, so early adopters always get the locked-in rate.
