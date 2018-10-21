from app import db
from app.helpers import page_title, redirect_non_admins
from app.models import User, Role
from app.user import bp
from app.user.forms import CreateUserForm, EditProfileForm, SettingsForm
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

no_perm = "index"

@bp.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template("user/profile.html", user=user, title=page_title("User profile"))

@bp.route("/edit/<username>", methods=["GET", "POST"])
@login_required
def edit(username):
    if current_user.has_admin_role() or current_user.username == username:
        form = EditProfileForm()

        if current_user.has_admin_role():
            role_choices = []

            all_roles = Role.query.all()
            for role in all_roles:
                role_choices.append((str(role.id), role.name))

            form.roles.choices = role_choices
        else:
            del form.roles

        user = User.query.filter_by(username=username).first_or_404()

        if form.validate_on_submit():
            user.about = form.about.data

            if(form.password.data):
                user.set_password(form.password.data)

                if current_user.username == user.username:
                    user.must_change_password = False
                elif current_user.has_admin_role():
                    # user must reset password after it has been changed by an admin
                    user.must_change_password = True

            if current_user.has_admin_role():
                new_user_roles = Role.query.filter(Role.id.in_(form.roles.data)).all()

                admin_role = Role.query.get(1)

                if username == current_user.username and current_user.has_admin_role() and admin_role not in new_user_roles:
                    new_user_roles.append(admin_role)
                    flash("You can't revoke your own admin role.", "danger")

                if user.id == 1 and admin_role not in new_user_roles:
                    new_user_roles.append(admin_role)
                    flash("The original admin can't be removed.", "danger")

                user.roles = new_user_roles

            db.session.commit()
            flash("Your changes have been saved.", "success")

            return redirect(url_for("user.profile", username=username))
        elif request.method == "GET":
            form.about.data = user.about

            if current_user.has_admin_role():
                user_roles = []
                for role in user.roles:
                    user_roles.append(str(role.id))

                form.roles.data = user_roles

        return render_template("user/edit.html", form=form, user=user, title=page_title("Edit profile"))
    else:
        flash("You dont have the neccessary role to perform this action.", "danger")
        return redirect(url_for(no_perm))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    form = CreateUserForm()

    role_choices = []

    all_roles = Role.query.all()
    for role in all_roles:
        role_choices.append((str(role.id), role.name))

    form.roles.choices = role_choices

    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        new_user_roles = Role.query.filter(Role.id.in_(form.roles.data)).all()
        new_user.roles = new_user_roles

        new_user.created = datetime.utcnow()

        db.session.add(new_user)
        db.session.commit()

        flash("New user " + new_user.username + " created.", "success")
        return redirect(url_for('user.list'))
    else:
        return render_template("user/create.html", form=form, title=page_title("Create new user"))

@bp.route("/list")
@login_required
def list():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    users = User.query.all()

    return render_template("user/list.html", users=users, title=page_title("User list"))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        current_user.dateformat = form.dateformat.data
        current_user.phb_session = form.phb_session.data
        current_user.phb_wiki = form.phb_wiki.data
        current_user.phb_character = form.phb_character.data
        current_user.phb_party = form.phb_party.data
        current_user.phb_calendar = form.phb_calendar.data

        flash("Settings changed.", "success")

        db.session.commit()
    elif request.method == "GET":
        form.dateformat.data = current_user.dateformat
        form.phb_session.data = current_user.phb_session
        form.phb_wiki.data = current_user.phb_wiki
        form.phb_character.data = current_user.phb_character
        form.phb_party.data = current_user.phb_party
        form.phb_calendar.data = current_user.phb_calendar

    return render_template("user/settings.html", form=form, title=page_title("User settings"))