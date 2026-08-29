from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, CodingProfile
from app.services.leetcode import get_user_stats

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    profiles = CodingProfile.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, profiles=profiles)

@main.route('/connect-profile', methods=['GET', 'POST'])
@login_required
def connect_profile():
    if request.method == 'POST':
        platform = request.form.get('platform', '').strip()
        username = request.form.get('username', '').strip()

        if not platform or not username:
            flash('Please select a platform and enter a username.', 'error')
            return redirect(url_for('main.connect_profile'))

        # Check if already connected
        existing = CodingProfile.query.filter_by(
            user_id=current_user.id,
            platform=platform
        ).first()

        if existing:
            flash(f'{platform.title()} account already connected.', 'error')
            return redirect(url_for('main.dashboard'))

        # Verify username exists on LeetCode
        if platform == 'leetcode':
            stats = get_user_stats(username)
            if not stats:
                flash('LeetCode username not found. Please check and try again.', 'error')
                return redirect(url_for('main.connect_leetcode'))

        profile = CodingProfile(
            user_id=current_user.id,
            platform=platform,
            platform_username=username
        )
        db.session.add(profile)
        db.session.commit()

        flash(f'{platform.title()} profile connected successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('connect_profile.html')