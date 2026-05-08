from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    event_type = db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instagram = db.Column(db.String(60), nullable=True)
    card_option = db.Column(db.String(20), nullable=False)
    design_style = db.Column(db.String(20), nullable=True)
    image_filename = db.Column(db.String(120), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- EMAIL NOTIFICATION ---
def send_notification(event_title):
    try:
        sender = os.environ.get('NOTIFY_EMAIL')
        password = os.environ.get('NOTIFY_PASSWORD')
        recipient = os.environ.get('NOTIFY_EMAIL')

        msg = MIMEText(f'A new event "{event_title}" has been submitted and is waiting for your approval.\n\nReview it at: http://127.0.0.1:5000/admin/review')
        msg['Subject'] = 'New NWA Car Events Submission'
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP_SSL('wyatt.schraeder@gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
        print(f"Email notification failed: {e}")

# --- ROUTES ---
@app.route("/")
def home():
    approved_events = Event.query.filter_by(approved=True).all()
    return render_template("index.html", events=approved_events)

@app.route("/calendar")
def calendar():
    approved_events = Event.query.filter_by(approved=True).all()
    events_list = [
        {
            "id": e.id,
            "title": e.title,
            "event_type": e.event_type,
            "date": e.date,
            "time": e.time,
            "location": e.location,
            "description": e.description or "",
            "instagram": e.instagram or "",
            "image_filename": e.image_filename or ""
        }
        for e in approved_events
    ]
    return render_template("calendar.html", events=events_list)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        title = request.form.get("title")
        event_type = request.form.get("event_type")
        date = request.form.get("date")
        time = request.form.get("time")
        location = request.form.get("location")
        description = request.form.get("description")
        instagram = request.form.get("instagram")
        card_option = request.form.get("card_option")
        design_style = request.form.get("design_style")

        image_filename = None
        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            image_filename = image_file.filename
            image_file.save(os.path.join("static/images", image_filename))

        new_event = Event(
            title=title,
            event_type=event_type,
            date=date,
            time=time,
            location=location,
            description=description,
            instagram=instagram,
            card_option=card_option,
            design_style=design_style,
            image_filename=image_filename
        )

        db.session.add(new_event)
        db.session.commit()

        send_notification(title)
        return redirect(url_for("submitted"))

    return render_template("submit.html")

@app.route("/submitted")
def submitted():
    return render_template("submitted.html")

@app.route("/event/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("event_detail.html", event=event)

@app.route("/admin/review")
def admin_review():
    pending = Event.query.filter_by(approved=False).all()
    approved = Event.query.filter_by(approved=True).all()
    return render_template("admin.html", pending=pending, approved=approved)

@app.route("/admin/approve/<int:event_id>")
def approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.approved = True
    db.session.commit()
    return redirect(url_for("admin_review"))

@app.route("/admin/delete/<int:event_id>")
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("admin_review"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import send_from_directory

@app.route("/admin/download/<int:event_id>")
def download_image(event_id):
    event = Event.query.get_or_404(event_id)
    if event.image_filename:
        directory = os.path.join(app.root_path, "static/images")
        return send_from_directory(directory, event.image_filename, as_attachment=True)
    return redirect(url_for("admin_review"))

@app.route("/admin/upload_card/<int:event_id>", methods=["POST"])
def upload_card(event_id):
    event = Event.query.get_or_404(event_id)
    card_file = request.files.get("card")
    if card_file and card_file.filename != "":
        os.makedirs("static/images/cards", exist_ok=True)
        filename = f"card_{event.id}.jpg"
        card_file.save(os.path.join("static/images/cards", filename))
        event.image_filename = f"cards/{filename}"
        db.session.commit()
    return redirect(url_for("admin_review"))