========================================
  EMAIL SETUP GUIDE
  Indian Culture Website
========================================

When someone submits the contact form, TWO emails are sent:
  1. Notification email → to you (admin) with full message details
  2. Confirmation email → to the visitor thanking them

----------------------------------------
STEP 1: Create a Gmail App Password
----------------------------------------
Gmail requires an "App Password" instead of your normal password.

1. Go to your Google Account:
   https://myaccount.google.com/security

2. Make sure "2-Step Verification" is ON
   (Security > 2-Step Verification)

3. Search for "App passwords" on the same page
   OR go to: https://myaccount.google.com/apppasswords

4. Select:
   - App: "Mail"
   - Device: "Windows Computer" (or any name)

5. Click "Generate" — you'll get a 16-character password
   Example: abcd efgh ijkl mnop

6. Copy that password (no spaces needed)

----------------------------------------
STEP 2: Set your App Password in app.py
----------------------------------------
Open app.py and find this line (~line 20):

    GMAIL_PASS = os.environ.get('GMAIL_PASS', 'YOUR_APP_PASSWORD_HERE')

Replace YOUR_APP_PASSWORD_HERE with your 16-character app password:

    GMAIL_PASS = os.environ.get('GMAIL_PASS', 'abcdefghijklmnop')

Your Gmail username and admin email are already set to:
    sudarshankalashetty8@gmail.com

----------------------------------------
STEP 3: Install and Run
----------------------------------------
pip install -r requirements.txt --upgrade
python init_db.py
python app.py

----------------------------------------
TROUBLESHOOTING
----------------------------------------
If emails are not sending:
- Make sure 2-Step Verification is ON in your Google account
- Double-check the App Password (no spaces)
- Check that your Gmail account has not blocked the sign-in
- The form still SAVES messages to the database even if email fails
  → Visit http://127.0.0.1:5000/admin to see all messages

========================================
