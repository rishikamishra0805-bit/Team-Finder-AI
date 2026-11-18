
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user, logout_user, login_required, current_user
)

from app import db
from app.models import (
    User, Project, JoinRequest, TeamMember, Notification
)
from app.matching import match_candidate


main = Blueprint("main", __name__)


# ==========================================
# NOTIFICATION HELPER
# ==========================================

def create_notification(user_id, message, link=""):
    notification = Notification(
        user_id=user_id,
        message=message,
        link=link,
        is_read=False
    )
    db.session.add(notification)


# ==========================================
# HOME PAGE
# ==========================================

@main.route("/")
def index():

    if not current_user.is_authenticated:
        return redirect(url_for("main.login"))

    projects = Project.query.order_by(
        Project.created_at.desc()
    ).limit(6).all()

    return render_template("index.html", projects=projects)


# ==========================================
# REGISTRATION
# ==========================================

@main.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:
            flash(
                "Please enter your name, valid email and a password of at least 6 characters.",
                "error"
            )

        elif User.query.filter_by(email=email).first():
            flash("This email is already registered.", "error")

        else:
            user = User(name=name, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)

            flash(
                "Account created! Complete your profile to get better matches.",
                "success"
            )

            return redirect(url_for("main.profile"))

    return render_template("register.html")


# ==========================================
# LOGIN
# ==========================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("main.dashboard"))

        flash("Email or password is incorrect.", "error")

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@main.route("/logout")
@login_required
def logout():

    logout_user()
    flash("You have been logged out successfully.", "success")

    return redirect(url_for("main.login"))


# ==========================================
# NOTIFICATIONS
# ==========================================

@main.route("/notifications")
@login_required
def notifications():

    notifications_list = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()

    return render_template(
        "notifications.html",
        notifications=notifications_list,
        unread_count=unread_count
    )


@main.route("/notifications/<int:notification_id>/open")
@login_required
def open_notification(notification_id):

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()

    notification.is_read = True
    db.session.commit()

    if notification.link:
        return redirect(notification.link)

    return redirect(url_for("main.notifications"))


@main.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():

    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({"is_read": True})

    db.session.commit()

    flash("All notifications marked as read.", "success")

    return redirect(url_for("main.notifications"))


# ==========================================
# DASHBOARD
# ==========================================

@main.route("/dashboard")
@login_required
def dashboard():

    projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    my_projects = Project.query.filter_by(
        creator_id=current_user.id
    ).order_by(
        Project.created_at.desc()
    ).all()

    my_project_ids = [project.id for project in my_projects]

    recommendations = []

    for project in projects:

        if project.creator_id == current_user.id:
            continue

        score, parts, reasons = match_candidate(
            current_user,
            project
        )

        recommendations.append((project, score, reasons))

    recommendations.sort(
        key=lambda item: item[1],
        reverse=True
    )

    received_requests = []

    if my_project_ids:

        requests_received = JoinRequest.query.filter(
            JoinRequest.project_id.in_(my_project_ids),
            JoinRequest.status == "Pending"
        ).order_by(
            JoinRequest.created_at.desc()
        ).all()

        for join_request in requests_received:

            request_user = db.session.get(
                User, join_request.user_id
            )

            request_project = db.session.get(
                Project, join_request.project_id
            )

            if request_user and request_project:
                received_requests.append(
                    (join_request, request_user, request_project)
                )

    team_memberships = []

    my_memberships = TeamMember.query.filter_by(
        user_id=current_user.id
    ).order_by(
        TeamMember.joined_at.desc()
    ).all()

    for membership in my_memberships:

        team_project = db.session.get(
            Project, membership.project_id
        )

        if team_project:
            team_memberships.append((membership, team_project))

    return render_template(
        "dashboard.html",
        recommendations=recommendations[:10],
        my_projects=my_projects,
        received_requests=received_requests,
        team_memberships=team_memberships,
        recommended_count=len(recommendations),
        created_count=len(my_projects),
        team_count=len(team_memberships),
        pending_requests_count=len(received_requests)
    )


# ==========================================
# USER PROFILE
# ==========================================

@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        fields = [
            "education",
            "skills",
            "interests",
            "preferred_role",
            "experience",
            "availability",
            "goals",
            "work_preference",
            "bio"
        ]

        for field in fields:
            setattr(
                current_user,
                field,
                request.form.get(field, "").strip()
            )

        db.session.commit()

        flash("Profile saved successfully.", "success")

        return redirect(url_for("main.profile"))

    return render_template("profile.html")


# ==========================================
# EXPLORE PROJECTS
# ==========================================

@main.route("/projects")
@login_required
def projects():

    items = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    match_scores = {}
    team_counts = {}

    for project in items:

        team_count = TeamMember.query.filter_by(
            project_id=project.id
        ).count()

        team_counts[project.id] = team_count

        if project.creator_id == current_user.id:
            match_scores[project.id] = None
        else:
            score, parts, reasons = match_candidate(
                current_user,
                project
            )
            match_scores[project.id] = score

    sort_by = request.args.get("sort", "newest")

    if sort_by == "match":

        items.sort(
            key=lambda project: (
                match_scores[project.id] is not None,
                match_scores[project.id] or 0
            ),
            reverse=True
        )

    return render_template(
        "projects.html",
        projects=items,
        match_scores=match_scores,
        team_counts=team_counts,
        sort_by=sort_by
    )


# ==========================================
# CREATE NEW PROJECT
# ==========================================

@main.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not description:
            flash(
                "Project title and description are required.",
                "error"
            )

        else:

            project = Project(
                title=title,
                description=description,
                creator_id=current_user.id,
                required_skills=request.form.get("required_skills", ""),
                roles_needed=request.form.get("roles_needed", ""),
                interests=request.form.get("interests", ""),
                experience=request.form.get("experience", "Beginner"),
                availability=request.form.get("availability", "Flexible"),
                goals=request.form.get("goals", ""),
                work_preference=request.form.get("work_preference", "Remote")
            )

            db.session.add(project)
            db.session.commit()

            flash(
                "Project published! Matching candidates can now discover it.",
                "success"
            )

            return redirect(url_for("main.projects"))

    return render_template("new_project.html")


# ==========================================
# STUDENT SENDS JOIN REQUEST
# ==========================================

@main.route("/projects/<int:project_id>/join", methods=["POST"])
@login_required
def request_to_join(project_id):

    project = Project.query.get_or_404(project_id)

    if project.creator_id == current_user.id:
        flash("You cannot join your own project.", "error")
        return redirect(
            url_for("main.project_detail", project_id=project.id)
        )

    existing_member = TeamMember.query.filter_by(
        user_id=current_user.id,
        project_id=project.id
    ).first()

    if existing_member:
        flash("You are already a member of this project.", "info")
        return redirect(
            url_for("main.project_detail", project_id=project.id)
        )

    existing = JoinRequest.query.filter_by(
        user_id=current_user.id,
        project_id=project.id
    ).first()

    if existing:

        if existing.status == "Rejected":

            existing.status = "Pending"

            create_notification(
                project.creator_id,
                f"{current_user.name} has sent a new join request for {project.title}.",
                url_for("main.project_detail", project_id=project.id)
            )

            db.session.commit()

            flash("Your join request has been sent again.", "success")

        elif existing.status == "Accepted":
            flash("Your request has already been accepted.", "info")

        else:
            flash("You have already sent a request for this project.", "info")

    else:

        new_request = JoinRequest(
            user_id=current_user.id,
            project_id=project.id,
            status="Pending"
        )

        db.session.add(new_request)

        create_notification(
            project.creator_id,
            f"{current_user.name} has requested to join {project.title}.",
            url_for("main.project_detail", project_id=project.id)
        )

        db.session.commit()

        flash("Join request sent successfully!", "success")

    return redirect(
        url_for("main.project_detail", project_id=project.id)
    )


# ==========================================
# CREATOR ACCEPTS OR REJECTS JOIN REQUEST
# ==========================================

@main.route("/join-request/<int:request_id>/<action>", methods=["POST"])
@login_required
def join_request_action(request_id, action):

    join_request = JoinRequest.query.get_or_404(request_id)

    project = Project.query.get_or_404(
        join_request.project_id
    )

    if project.creator_id != current_user.id:
        flash("You are not authorized to manage this request.", "error")
        return redirect(url_for("main.dashboard"))

    if action not in ["accept", "reject"]:
        flash("Invalid action.", "error")

    elif join_request.status != "Pending":
        flash("This request has already been processed.", "info")

    elif action == "accept":

        member = TeamMember.query.filter_by(
            user_id=join_request.user_id,
            project_id=project.id
        ).first()

        if not member:
            member = TeamMember(
                user_id=join_request.user_id,
                project_id=project.id,
                role="Member"
            )
            db.session.add(member)

        join_request.status = "Accepted"

        create_notification(
            join_request.user_id,
            f"Your request to join {project.title} has been accepted!",
            url_for("main.project_detail", project_id=project.id)
        )

        db.session.commit()

        flash("Candidate accepted! They are now a team member.", "success")

    elif action == "reject":

        join_request.status = "Rejected"

        create_notification(
            join_request.user_id,
            f"Your request to join {project.title} was not accepted.",
            url_for("main.project_detail", project_id=project.id)
        )

        db.session.commit()

        flash("Join request rejected.", "info")

    return redirect(
        url_for("main.project_detail", project_id=project.id)
    )


# ==========================================
# PROJECT DETAILS AND MATCHING
# ==========================================

@main.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):

    project = Project.query.get_or_404(project_id)

    matches = []
    join_requests = []
    request_entries = []
    team_members = []
    own_match = None
    own_request = None
    is_team_member = False

    team_records = TeamMember.query.filter_by(
        project_id=project.id
    ).order_by(
        TeamMember.joined_at.asc()
    ).all()

    for member in team_records:

        member_user = db.session.get(
            User, member.user_id
        )

        if member_user:
            team_members.append((member, member_user))

    if project.creator_id == current_user.id:

        users = User.query.filter(
            User.id != project.creator_id
        ).all()

        for user in users:

            score, parts, reasons = match_candidate(
                user, project
            )

            matches.append((user, score, reasons))

        matches.sort(
            key=lambda item: item[1],
            reverse=True
        )

        join_requests = JoinRequest.query.filter_by(
            project_id=project.id
        ).order_by(
            JoinRequest.created_at.desc()
        ).all()

        for join_request in join_requests:

            request_user = db.session.get(
                User, join_request.user_id
            )

            if request_user:
                request_entries.append((join_request, request_user))

    else:

        score, parts, reasons = match_candidate(
            current_user, project
        )

        own_match = (score, reasons)

        own_request = JoinRequest.query.filter_by(
            user_id=current_user.id,
            project_id=project.id
        ).first()

        is_team_member = TeamMember.query.filter_by(
            user_id=current_user.id,
            project_id=project.id
        ).first() is not None

    return render_template(
        "project_detail.html",
        project=project,
        matches=matches[:10],
        join_requests=join_requests,
        request_entries=request_entries,
        team_members=team_members,
        own_match=own_match,
        own_request=own_request,
        is_team_member=is_team_member
    )
