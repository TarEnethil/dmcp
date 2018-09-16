from app import db
from app.helpers import page_title, redirect_non_admins, get_next_epoch_order, get_next_month_order, get_next_day_order, calendar_sanity_check, gen_calendar_preview_data
from app.models import CalendarSetting, Epoch, Month, Day
from app.calendar import bp
from app.calendar.forms import EpochForm, MonthForm, DayForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

no_perm = "index"

@bp.route("/settings", methods=["GET"])
@login_required
def settings():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)

    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()

    return render_template("calendar/settings.html", settings=cset, epochs=epochs, months=months, days=days, title=page_title("Calendar settings"))

@bp.route("/dummy", methods=["GET"])
@login_required
def dummy():
    return redirect(url_for("index"))

@bp.route("/view", methods=["GET"])
@login_required
def view():
    cset = CalendarSetting.query.get(1)
    epochs = None
    months = None
    days = None

    if cset.finalized == True:
        epochs = Epoch.query.order_by(Epoch.order.asc()).all()
        months = Month.query.order_by(Month.order.asc()).all()
        days = Day.query.order_by(Day.order.asc()).all()

    return render_template("calendar/view.html", settings=cset, epochs=epochs, months=months, days=days, title=page_title("View calendar"))

@bp.route("/check", methods=["GET"])
@login_required
def check():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    status = calendar_sanity_check()

    if status == True:
        flash("All checks have passed. The calendar works with this configuration.", "success", "danger")
    else:
        flash("There were errors checking the calendar. See the other messages for more details.", "danger", "danger")

    return redirect(url_for("calendar.settings"))

@bp.route("/preview", methods=["GET"])
@login_required
def preview():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    status = calendar_sanity_check()

    if status == False:
        flash("There were errors previewing the calendar. See the other messages for more details.", "danger", "danger")
        return redirect(url_for("calendar.settings"))

    stats = gen_calendar_preview_data()

    return render_template("calendar/preview.html", stats=stats, title=page_title("Preview calendar"))

@bp.route("/finalize", methods=["GET"])
@login_required
def finalize():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    status = calendar_sanity_check()

    if status == False:
        flash("There were errors finalizing the calendar. See the other messages for more details.", "danger", "danger")
        return redirect(url_for("calendar.settings"))

    gen_calendar_preview_data(commit=True)
    cset = CalendarSetting.query.get(1)
    cset.finalized = True
    db.session.commit()

    flash("The calendar was finalized.", "success", "danger")
    return redirect(url_for('calendar.settings'))

@bp.route("/epoch/create", methods=["GET", "POST"])
@login_required
def epoch_create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new epochs.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create new epoch"
    form = EpochForm()


    if form.validate_on_submit():
        order_num = get_next_epoch_order()

        new_epoch = Epoch(name=form.name.data, abbreviation=form.abbreviation.data, description=form.description.data, years=form.years.data, circa=form.circa.data, order=order_num)

        db.session.add(new_epoch)
        db.session.commit()

        flash("Epoch added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new epoch"))

@bp.route("/epoch/edit/<int:id>", methods=["GET", "POST"])
@login_required
def epoch_edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit epoch"
    form = EpochForm()

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        del form.years
        del form.circa

    epoch = Epoch.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        epoch.name = form.name.data
        epoch.abbreviation = form.abbreviation.data
        epoch.description = form.description.data

        if cset.finalized == False:
            epoch.years = form.years.data
            epoch.circa = form.circa.data

        db.session.commit()

        flash("Epoch edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = epoch.name
        form.abbreviation.data = epoch.abbreviation
        form.description.data = epoch.description

        if cset.finalized == False:
            form.years.data = epoch.years
            form.circa.data = epoch.circa

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Edit epoch"))

@bp.route("/epoch/delete/<int:id>", methods=["GET"])
@login_required
def epoch_delete(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't delete epochs.", "danger")
        return redirect(url_for('calendar.settings'))

    epoch = Epoch.query.filter_by(id=id).first_or_404()

    db.session.delete(epoch)
    db.session.commit()

    flash("Epoch was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/epoch/up/<int:id>", methods=["GET"])
@login_required
def epoch_up(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of epochs.", "danger")
        return redirect(url_for('calendar.settings'))

    epoch_to_up = Epoch.query.filter_by(id=id).first_or_404()
    epoch_to_down = Epoch.query.filter(Epoch.order < epoch_to_up.order).order_by(Epoch.order.desc()).limit(1).first()

    if not epoch_to_down:
        flash("No epoch with lower order found.", "danger")
        return redirect(url_for("calendar.settings"))

    up_order = epoch_to_up.order
    down_order = epoch_to_down.order

    epoch_to_up.order = down_order
    epoch_to_down.order = up_order

    db.session.commit()

    flash("Order of '" + epoch_to_up.name + "' and '" + epoch_to_down.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/epoch/down/<int:id>", methods=["GET"])
@login_required
def epoch_down(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of epochs.", "danger")
        return redirect(url_for('calendar.settings'))

    epoch_to_down = Epoch.query.filter_by(id=id).first_or_404()
    epoch_to_up = Epoch.query.filter(Epoch.order > epoch_to_down.order).order_by(Epoch.order.asc()).limit(1).first()

    if not epoch_to_up:
        flash("No epoch with higher order found.", "danger")
        return redirect(url_for("calendar.settings"))

    down_order = epoch_to_down.order
    up_order = epoch_to_up.order

    epoch_to_down.order = up_order
    epoch_to_up.order = down_order

    db.session.commit()

    flash("Order of '" + epoch_to_down.name + "' and '" + epoch_to_up.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/month/create", methods=["GET", "POST"])
@login_required
def month_create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new months.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create new month"
    form = MonthForm()

    if form.validate_on_submit():
        order_num = get_next_month_order()

        new_month = Month(name=form.name.data, abbreviation=form.abbreviation.data, description=form.description.data, days=form.days.data, order=order_num)

        db.session.add(new_month)
        db.session.commit()

        flash("Month added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new month"))

@bp.route("/month/edit/<int:id>", methods=["GET", "POST"])
@login_required
def month_edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit month"
    form = MonthForm()

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        del form.days

    month = Month.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        month.name = form.name.data
        month.abbreviation = form.abbreviation.data
        month.description = form.description.data

        if cset.finalized == False:
            month.days = form.days.data

        db.session.commit()

        flash("Month edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = month.name
        form.abbreviation.data = month.abbreviation
        form.description.data = month.description

        if cset.finalized == False:
            form.days.data = month.days

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Edit month"))

@bp.route("/month/delete/<int:id>", methods=["GET"])
@login_required
def month_delete(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't deletet months.", "danger")
        return redirect(url_for('calendar.settings'))

    month = Month.query.filter_by(id=id).first_or_404()

    db.session.delete(month)
    db.session.commit()

    flash("Month was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/month/up/<int:id>", methods=["GET"])
@login_required
def month_up(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of months.", "danger")
        return redirect(url_for('calendar.settings'))

    month_to_up = Month.query.filter_by(id=id).first_or_404()
    month_to_down = Month.query.filter(Month.order < month_to_up.order).order_by(Month.order.desc()).limit(1).first()

    if not month_to_down:
        flash("No month with lower order found.", "danger")
        return redirect(url_for("calendar.settings"))

    up_order = month_to_up.order
    down_order = month_to_down.order

    month_to_up.order = down_order
    month_to_down.order = up_order

    db.session.commit()

    flash("Order of '" + month_to_up.name + "' and '" + month_to_down.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/month/down/<int:id>", methods=["GET"])
@login_required
def month_down(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of months.", "danger")
        return redirect(url_for('calendar.settings'))

    month_to_down = Month.query.filter_by(id=id).first_or_404()
    month_to_up = Month.query.filter(Month.order > month_to_down.order).order_by(Month.order.asc()).limit(1).first()

    if not month_to_up:
        flash("No month with higher order found.", "danger")
        return redirect(url_for("calendar.settings"))

    down_order = month_to_down.order
    up_order = month_to_up.order

    month_to_down.order = up_order
    month_to_up.order = down_order

    db.session.commit()

    flash("Order of '" + month_to_down.name + "' and '" + month_to_up.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/day/create", methods=["GET", "POST"])
@login_required
def day_create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new days.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create new day"
    form = DayForm()

    if form.validate_on_submit():
        order_num = get_next_day_order()

        new_day = Day(name=form.name.data, abbreviation=form.abbreviation.data, description=form.description.data, order=order_num)

        db.session.add(new_day)
        db.session.commit()

        flash("Day added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new day"))

@bp.route("/day/edit/<int:id>", methods=["GET", "POST"])
@login_required
def day_edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit day"
    form = DayForm()

    day = Day.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        day.name = form.name.data
        day.abbreviation = form.abbreviation.data
        day.description = form.description.data

        db.session.commit()

        flash("day edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = day.name
        form.abbreviation.data = day.abbreviation
        form.description.data = day.description

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Edit day"))

@bp.route("/day/delete/<int:id>", methods=["GET"])
@login_required
def day_delete(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't delete days.", "danger")
        return redirect(url_for('calendar.settings'))

    day = Day.query.filter_by(id=id).first_or_404()

    db.session.delete(day)
    db.session.commit()

    flash("Day was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/day/up/<int:id>", methods=["GET"])
@login_required
def day_up(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of days.", "danger")
        return redirect(url_for('calendar.settings'))

    day_to_up = Day.query.filter_by(id=id).first_or_404()
    day_to_down = Day.query.filter(Day.order < day_to_up.order).order_by(Day.order.desc()).limit(1).first()

    if not day_to_down:
        flash("No day with lower order found.", "danger")
        return redirect(url_for("calendar.settings"))

    up_order = day_to_up.order
    down_order = day_to_down.order

    day_to_up.order = down_order
    day_to_down.order = up_order

    db.session.commit()

    flash("Order of '" + day_to_up.name + "' and '" + day_to_down.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/day/down/<int:id>", methods=["GET"])
@login_required
def day_down(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of days.", "danger")
        return redirect(url_for('calendar.settings'))

    day_to_down = Day.query.filter_by(id=id).first_or_404()
    day_to_up = Day.query.filter(Day.order > day_to_down.order).order_by(Day.order.asc()).limit(1).first()

    if not day_to_up:
        flash("No day with higher order found.", "danger")
        return redirect(url_for("calendar.settings"))

    down_order = day_to_down.order
    up_order = day_to_up.order

    day_to_down.order = up_order
    day_to_up.order = down_order

    db.session.commit()

    flash("Order of '" + day_to_down.name + "' and '" + day_to_up.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))