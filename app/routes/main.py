from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, CodingProfile, Problem, ProblemSession, Attempt
from app.services.leetcode import get_user_stats, get_problem

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


@main.route('/start-session', methods=['GET', 'POST'])
@login_required
def start_session():
    if request.method == 'POST':
        platform = request.form.get('platform', '').strip()

        if not platform:
            flash('Please select a platform.', 'error')
            return redirect(url_for('main.start_session'))

        if platform == 'leetcode':
            identifier = request.form.get('lc_identifier', '').strip().lower()

            if not identifier:
                flash('Please enter a problem number or slug.', 'error')
                return redirect(url_for('main.start_session'))

            # Check if it's a number
            if identifier.isdigit():
                # Look up in DB first by external_id
                problem = Problem.query.filter_by(
                    platform='leetcode',
                    external_id=identifier
                ).first()

                if not problem:
                    flash('Problem number not in our database yet. Please enter the problem slug instead.', 'error')
                    return redirect(url_for('main.start_session'))
            else:
                # Treat as slug
                problem = Problem.query.filter_by(
                    platform='leetcode',
                    title_slug=identifier
                ).first()

                if not problem:
                    data = get_problem(identifier)
                    if not data:
                        flash('Problem not found on LeetCode. Check the slug and try again.', 'error')
                        return redirect(url_for('main.start_session'))

                    problem = Problem(
                        platform='leetcode',
                        external_id=data['questionId'],
                        title=data['title'],
                        title_slug=data['titleSlug'],
                        description=data['content'],
                        difficulty=data['difficulty'],
                        tags=[tag['name'] for tag in data.get('topicTags', [])],
                        examples=data.get('examples', []),
                        constraints=[]
                    )
                    db.session.add(problem)
                    db.session.flush()

        else:
            # Other platforms — manual input
            title_slug = request.form.get('title_slug', '').strip()
            problem_title = request.form.get('problem_title', '').strip() or title_slug
            problem_description = request.form.get('problem_statement', '').strip()
            examples_text = request.form.get('examples', '').strip()
            constraints_text = request.form.get('constraints', '').strip()

            if not title_slug:
                flash('Please enter the problem slug.', 'error')
                return redirect(url_for('main.start_session'))

            if not problem_description:
                flash('Problem statement is required.', 'error')
                return redirect(url_for('main.start_session'))

            problem = Problem.query.filter_by(
                platform=platform,
                title_slug=title_slug
            ).first()

            if not problem:
                problem = Problem(
                    platform=platform,
                    external_id=title_slug,
                    title=problem_title,
                    title_slug=title_slug,
                    description=problem_description,
                    examples=examples_text,
                    constraints=constraints_text,
                    difficulty='Unknown',
                    tags=[]
                )
                db.session.add(problem)
                db.session.flush()

        # Check for existing active session
        existing_session = ProblemSession.query.filter_by(
            user_id=current_user.id,
            problem_id=problem.id,
            status='in_progress'
        ).first()

        if existing_session:
            flash('You already have an active session for this problem.', 'info')
            return redirect(url_for('main.session', session_id=existing_session.id))

        new_session = ProblemSession(
            user_id=current_user.id,
            problem_id=problem.id,
            status='in_progress'
        )
        db.session.add(new_session)
        db.session.commit()

        flash(f'Session started for {problem.title}.', 'success')
        return redirect(url_for('main.session', session_id=new_session.id))

    return render_template('start_session.html')


@main.route('/session/<int:session_id>')
@login_required
def session(session_id):
    problem_session = ProblemSession.query.filter_by(
        id=session_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template('session.html', 
                         session=problem_session,
                         problem=problem_session.problem,
                         attempts=problem_session.attempts)


@main.route('/session/<int:session_id>/submit', methods=['POST'])
@login_required
def submit_attempt(session_id):
    problem_session = ProblemSession.query.filter_by(
        id=session_id,
        user_id=current_user.id
    ).first_or_404()

    if problem_session.status != 'in_progress':
        flash('This problem session is no longer active.', 'error')
        return redirect(url_for('main.session', session_id=session_id))

    code = request.form.get('code', '').strip()
    language = request.form.get('language', '').strip().lower()
    platform_verdict = request.form.get('platfrom_verdict', '').strip()

    if not code:
        flash('Please enter your code before submitting.', 'error')
        return redirect(url_for('main.session', session_id=session_id))

    if not language:
        flash('Please select a programming language.', 'error')
        return redirect(url_for('main.session', session_id=session_id))

    # Calculate the attempt number
    attempt_number = Attempt.query.filter_by(
        session_id=problem_session.id
    ).count() + 1

    attempt = Attempt(
        session_id=problem_session.id,
        code=code,
        language=language,
        platform_verdict=platform_verdict,
        attempt_number=attempt_number
    )

    db.session.add(attempt)
    db.session.commit()

    flash(f'Attempt #{attempt_number} submitted successfully.', 'success')

    return redirect(url_for(
        'main.session',
        session_id=session_id
    ))