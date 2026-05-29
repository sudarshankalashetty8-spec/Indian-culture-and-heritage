from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message as MailMessage
from datetime import datetime
import os

app = Flask(__name__)

# ── Database ──────────────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///indian_culture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Email (Gmail SMTP) ────────────────────────────────────
# Replace these values or set them as environment variables
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'sudarshankalashetty8@gmail.com')
GMAIL_USER  = os.environ.get('GMAIL_USER',  'sudarshankalashetty8@gmail.com')
GMAIL_PASS  = os.environ.get('GMAIL_PASS',  'YOUR_APP_PASSWORD_HERE')

app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = GMAIL_USER
app.config['MAIL_PASSWORD']       = GMAIL_PASS
app.config['MAIL_DEFAULT_SENDER'] = GMAIL_USER

db   = SQLAlchemy(app)
mail = Mail(app)


# ── Models ────────────────────────────────────────────────
class CultureItem(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    category    = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location    = db.Column(db.String(200))
    state       = db.Column(db.String(100))
    image_url   = db.Column(db.String(500))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'category': self.category,
            'description': self.description, 'location': self.location,
            'state': self.state, 'image_url': self.image_url
        }

class ContactMessage(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(200), nullable=False)
    email    = db.Column(db.String(200), nullable=False)
    subject  = db.Column(db.String(300), nullable=False)
    message  = db.Column(db.Text, nullable=False)
    sent_at  = db.Column(db.DateTime, default=datetime.utcnow)
    is_read  = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'email': self.email,
            'subject': self.subject, 'message': self.message,
            'sent_at': self.sent_at.strftime('%d %b %Y, %I:%M %p'),
            'is_read': self.is_read
        }


# ── Page routes ───────────────────────────────────────────
@app.route('/')
def home():      return render_template('index.html')

@app.route('/about')
def about():     return render_template('about.html')

@app.route('/contact')
def contact():   return render_template('contact.html')

@app.route('/timeline')
def timeline():  return render_template('timeline.html')

@app.route('/admin')
def admin():     return render_template('admin.html')


# ── Culture API ───────────────────────────────────────────
@app.route('/api/culture')
def get_culture():
    category = request.args.get('category')
    query = CultureItem.query
    if category:
        query = query.filter_by(category=category)
    return jsonify([i.to_dict() for i in query.all()])

@app.route('/api/culture/<int:item_id>')
def get_culture_item(item_id):
    return jsonify(CultureItem.query.get_or_404(item_id).to_dict())

@app.route('/api/categories')
def get_categories():
    cats = db.session.query(CultureItem.category).distinct().all()
    return jsonify([c[0] for c in cats])

@app.route('/api/search')
def search_culture():
    q        = request.args.get('q', '')
    category = request.args.get('category')
    sq = CultureItem.query.filter(
        CultureItem.name.ilike(f'%{q}%') |
        CultureItem.description.ilike(f'%{q}%')
    )
    if category:
        sq = sq.filter_by(category=category)
    return jsonify([i.to_dict() for i in sq.all()])


# ── Contact / Email API ───────────────────────────────────
@app.route('/api/contact', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    name    = data.get('name',    '').strip()
    email   = data.get('email',   '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not all([name, email, subject, message]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400

    # 1️⃣  Save to database
    msg = ContactMessage(name=name, email=email, subject=subject, message=message)
    db.session.add(msg)
    db.session.commit()

    email_sent = False
    email_error = ''

    # 2️⃣  Send notification email to admin
    try:
        admin_mail = MailMessage(
            subject=f'[Indian Culture Website] New Message: {subject}',
            recipients=[ADMIN_EMAIL],
            reply_to=email,
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                        border:1px solid #ddd;border-radius:10px;overflow:hidden;">
              <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                          padding:24px 30px;color:white;">
                <h2 style="margin:0;">🇮🇳 New Contact Message</h2>
                <p style="margin:6px 0 0;opacity:.85;">Indian Culture &amp; Heritage Website</p>
              </div>
              <div style="padding:28px 30px;">
                <table style="width:100%;border-collapse:collapse;">
                  <tr><td style="padding:8px 0;color:#888;width:100px;"><b>Name</b></td>
                      <td style="padding:8px 0;color:#333;">{name}</td></tr>
                  <tr><td style="padding:8px 0;color:#888;"><b>Email</b></td>
                      <td style="padding:8px 0;"><a href="mailto:{email}" style="color:#764ba2;">{email}</a></td></tr>
                  <tr><td style="padding:8px 0;color:#888;"><b>Subject</b></td>
                      <td style="padding:8px 0;color:#333;">{subject}</td></tr>
                  <tr><td style="padding:8px 0;color:#888;"><b>Received</b></td>
                      <td style="padding:8px 0;color:#333;">{msg.sent_at.strftime('%d %b %Y at %I:%M %p')}</td></tr>
                </table>
                <div style="margin-top:20px;">
                  <p style="color:#888;font-size:13px;margin-bottom:8px;"><b>Message:</b></p>
                  <div style="background:#f8f9fa;border-left:4px solid #764ba2;
                              padding:16px 20px;border-radius:6px;color:#333;
                              line-height:1.7;">{message}</div>
                </div>
                <div style="margin-top:24px;text-align:center;">
                  <a href="mailto:{email}?subject=Re: {subject}"
                     style="background:linear-gradient(135deg,#667eea,#764ba2);
                            color:white;padding:12px 28px;border-radius:25px;
                            text-decoration:none;font-weight:600;display:inline-block;">
                    ↩️ Reply to {name}
                  </a>
                </div>
              </div>
              <div style="background:#f8f9fa;padding:16px 30px;text-align:center;
                          font-size:12px;color:#aaa;">
                Sharnbasava University, Gulbarga, Karnataka, India
              </div>
            </div>
            """
        )
        mail.send(admin_mail)
        email_sent = True
    except Exception as e:
        email_error = str(e)
        print(f"Email error: {e}")

    # 3️⃣  Send confirmation email to the sender
    try:
        confirm_mail = MailMessage(
            subject='Thank you for contacting us – Indian Culture Website',
            recipients=[email],
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                        border:1px solid #ddd;border-radius:10px;overflow:hidden;">
              <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                          padding:24px 30px;color:white;text-align:center;">
                <h2 style="margin:0;">🇮🇳 Indian Culture &amp; Heritage</h2>
                <p style="margin:6px 0 0;opacity:.85;">Sharnbasava University, Gulbarga</p>
              </div>
              <div style="padding:30px;">
                <p style="color:#333;font-size:16px;">Dear <b>{name}</b>,</p>
                <p style="color:#555;line-height:1.7;">
                  Thank you for reaching out! We have received your message and
                  will get back to you as soon as possible.
                </p>
                <div style="background:#f8f9fa;border-left:4px solid #667eea;
                            padding:16px 20px;border-radius:6px;margin:20px 0;">
                  <p style="margin:0 0 6px;color:#888;font-size:13px;"><b>Your message:</b></p>
                  <p style="margin:0;color:#555;font-style:italic;">{message}</p>
                </div>
                <p style="color:#555;line-height:1.7;">
                  For urgent queries, you can also reach us at:<br>
                  📧 <a href="mailto:sudarshankalashetty8@gmail.com" style="color:#764ba2;">sudarshankalashetty8@gmail.com</a><br>
                  📞 +91 8861238575
                </p>
              </div>
              <div style="background:#f8f9fa;padding:16px 30px;text-align:center;
                          font-size:12px;color:#aaa;">
                🇮🇳 Celebrating India's Rich Cultural Heritage
              </div>
            </div>
            """
        )
        mail.send(confirm_mail)
    except Exception as e:
        print(f"Confirmation email error: {e}")

    return jsonify({
        'success': True,
        'message': 'Message sent successfully!',
        'email_sent': email_sent,
        'email_error': email_error if not email_sent else ''
    })


# ── Messages API (admin) ──────────────────────────────────
@app.route('/api/messages')
def get_messages():
    msgs = ContactMessage.query.order_by(ContactMessage.sent_at.desc()).all()
    return jsonify([m.to_dict() for m in msgs])

@app.route('/api/messages/<int:msg_id>/read', methods=['POST'])
def mark_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
