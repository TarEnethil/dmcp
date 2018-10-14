from app import db
from flask import flash
from app.models import GeneralSetting, Character, Party, Session, WikiEntry, User, Role, Epoch, Month, Day, CalendarSetting, EventCategory, Event
from flask_login import current_user
from wtforms.validators import ValidationError
from sqlalchemy import and_, or_, not_
from collections import OrderedDict


def flash_no_permission(msg=None):
    if (msg != None):
        flash(msg)
    else:
        flash("No permission for this action.", "danger")

def redirect_non_admins():
    if not current_user.has_admin_role():
        flash_no_permission()
        return True
    return False

def redirect_non_wiki_admins():
    if not current_user.is_wiki_admin():
        flash_no_permission()
        return True
    return False

def redirect_non_event_admins():
    if not current_user.is_event_admin():
        flash_no_permission()
        return True
    return False

def page_title(dynamic_part=None):
    static_part = GeneralSetting.query.get(1).title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part

def gen_party_members_choices():
    choices = []

    characters = Character.query.all()

    for char in characters:
        choices.append((char.id, char.name + " ("+ char.player.username +")"))

    return choices

def gen_participant_choices():
    choices = []

    parties = Party.query.all()

    for party in parties:
        if len(party.members) == 0:
            continue

        p = (party.name, [])

        for member in party.members:
            p[1].append((member.id, member.name))

        choices.append(p)

    no_party_chars = Character.query.filter(Character.parties==None).all()

    if len(no_party_chars) > 0:
        p = ("No party", [])

        for char in no_party_chars:
            p[1].append((char.id, char.name))

        choices.append(p)

    return choices

def gen_wiki_entry_choices():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.with_entities(WikiEntry.category, WikiEntry.id, WikiEntry.title).order_by(WikiEntry.title.asc()).all()

    cat_dict = {}

    for entry in entries:
        if entry[0] not in cat_dict:
            cat_dict[entry[0]] = []

        cat_dict[entry[0]].append(entry[1:3])

    ordered = OrderedDict(sorted(cat_dict.items(), key=lambda t: t[0]))

    choices = [(0, "*no linked article*")]

    for k in ordered.keys():
        if k != "":
            p = (k, [])
        else:
            p = ("Main category", [])

        for choice in ordered[k]:
            p[1].append((choice[0], choice[1]))

        choices.append(p)

    return choices

def gen_event_category_choices():
    choices = []

    categories = EventCategory.query.all()

    for cat in categories:
        choices.append((cat.id, cat.name))

    return choices

def gen_epoch_choices():
    return [(e.id, e.name) for e in Epoch.query.order_by(Epoch.order.asc()).all()]

def gen_month_choices():
    return [(m.id, m.name) for m in Month.query.order_by(Month.order.asc()).all()]

def gen_day_choices(month_id):
    m = Month.query.filter_by(id=month_id).first()

    if m == None:
        return ([0, "ERROR month not found"])

    return [(n, n) for n in xrange(1, m.days + 1)]

def get_session_number(code):
    q = Session.query.filter(Session.code == code)
    return q.count()

def get_previous_session_id(date, code):
    q = Session.query.filter(and_(Session.code == code, Session.date < date)).order_by(Session.date.desc()).first()

    if q:
        return q.id
    else:
        return

def get_next_session_id(date, code):
    q = Session.query.filter(and_(Session.code == code, Session.date > date)).order_by(Session.date.asc()).first()

    if q:
        return q.id
    else:
        return

def get_next_epoch_order():
    q = Epoch.query.order_by(Epoch.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

def get_next_month_order():
    q = Month.query.order_by(Month.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

def get_next_day_order():
    q = Day.query.order_by(Day.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

def prepare_wiki_nav():
    if current_user.has_admin_role():
        entries = WikiEntry.query.filter(WikiEntry.id != 1)
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(WikiEntry.id != 1, not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(WikiEntry.id != 1, or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.with_entities(WikiEntry.category, WikiEntry.id, WikiEntry.title, WikiEntry.is_visible).order_by(WikiEntry.title.asc()).all()

    cat_dict = {}

    for entry in entries:
        if entry[0] not in cat_dict:
            cat_dict[entry[0]] = []

        cat_dict[entry[0]].append(entry[1:4])

    return OrderedDict(sorted(cat_dict.items(), key=lambda t: t[0]))

def search_wiki_text(text):
    if current_user.has_admin_role():
        entries = WikiEntry.query.filter(WikiEntry.content.contains(text))
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))), WikiEntry.content.contains(text))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id), WikiEntry.content.contains(text))

    entries = entries.with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.content).order_by(WikiEntry.edited.desc())

    return entries.all()

def get_search_context(term, entry_text):
    pos = entry_text.find(term)

    if pos == -1:
        return "ERROR, SHOULD NOT HAPPEN"

    left = max(0, pos - 25)
    right = min(pos + 25, len(entry_text))

    return entry_text[left:right]

def prepare_search_result(term, entries):
    results = []

    for entry in entries:
        if term in entry[2]:
            results.append((entry[0], entry[1], get_search_context(term, entry[2])))

    return results

def search_wiki_tag(tag):
    if current_user.has_admin_role():
        entries = WikiEntry.query.filter(WikiEntry.tags.contains(tag))
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))), WikiEntry.tags.contains(tag))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id), WikiEntry.tags.contains(tag))

    entries = entries.with_entities(WikiEntry.id, WikiEntry.title).order_by(WikiEntry.edited.desc()).all()

    return entries

def get_recently_created():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.join(User, WikiEntry.created_by_id == User.id).with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.created, User.username).order_by(WikiEntry.created.desc()).limit(5).all()

    return entries

def get_recently_edited():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.join(User, WikiEntry.edited_by_id == User.id).with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.edited, User.username).order_by(WikiEntry.edited.desc()).limit(5).all()

    return entries

def calendar_sanity_check():
    tests_passed = True

    cset = CalendarSetting.query.get(1)

    if cset.finalized == True:
        tests_passed = False
        flash("The calendar is already finalized.", "danger")

    epochs = Epoch.query.all()

    if not epochs:
        tests_passed = False
        flash("Calendar needs at least one epoch.", "danger")

    current_epoch = Epoch.query.order_by(Epoch.order.desc()).limit(1).first()

    if current_epoch.years != 0:
        tests_passed = False
        flash("The current epoch (" + current_epoch.name + ") needs a duration of 0.", "danger")

    all_other_epochs = Epoch.query.filter(Epoch.id != current_epoch.id).all()

    for epoch in all_other_epochs:
        if epoch.years == 0:
            tests_passed = False
            flash("All epochs except the current one need a duration > 0. '" + epoch.name + "' violates that constraint." , "danger")

    months = Month.query.all()

    if not months:
        tests_passed = False
        flash("Calendar needs at least one month.", "danger")

    days = Day.query.all()

    if not days:
        tests_passed = False
        flash("Calendar needs at least one day.", "danger")

    return tests_passed

def gen_calendar_preview_data(commit=False):
    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()

    for i, epoch in enumerate(epochs):
        if i > 0:
            epoch.years_before = epochs[i - 1].years_before + epochs[i - 1].years

    for i, month in enumerate(months):
        if i > 0:
            month.days_before = months[i - 1].days_before + months[i - 1].days

    if commit == True:
        db.session.commit()
    else:
        preview_info = {}
        preview_info["epochs"] = epochs
        preview_info["months"] = months
        preview_info["days"] = days

        preview_info["days_per_week"] = len(days)
        preview_info["days_per_year"] = months[-1].days_before + months[-1].days
        preview_info["months_per_year"] = len(months)

        return preview_info

def gen_calendar_stats():
    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()
    categories = EventCategory.query.all()

    stats = {}
    stats["epochs"] = epochs
    stats["months"] = months
    stats["days"] = days
    stats["categories"] = categories

    stats["days_per_week"] = len(days)
    stats["days_per_year"] = months[-1].days_before + months[-1].days
    stats["months_per_year"] = len(months)

    return stats

def update_timestamp(event_id):
    timestamp = 0
    ev = Event.query.filter_by(id=event_id).first()
    stats = gen_calendar_stats()

    if ev == None:
        return

    years = ev.epoch.years_before + (ev.year - 1)

    days_into_year = ev.month.days_before + ev.day

    timestamp = years * stats["days_per_year"] + days_into_year

    ev.timestamp = timestamp
    db.session.commit()

def get_epochs():
    e = Epoch.query.order_by(Epoch.order.asc()).all()

    return e

def get_years_in_epoch(e_id):
    q = Event.query.with_entities(Event.year).filter_by(epoch_id=e_id).group_by(Event.year).order_by(Event.year.asc()).all()

    return q

def get_events(filter_epoch=None, filter_year=None):
    if current_user.has_admin_role():
        events = Event.query
    elif current_user.has_event_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        events = Event.query.filter(not_(and_(Event.is_visible == False, Event.created_by_id.in_(admin_ids))))
    else:
        events = Event.query.filter(or_(Event.is_visible == True, Event.created_by_id == current_user.id))

    if filter_epoch and filter_year:
        events = events.filter_by(epoch_id = filter_epoch, year = filter_year)
    elif filter_epoch:
        events = events.filter_by(epoch_id = filter_epoch)

    events = events.order_by(Event.timestamp.asc()).all()

    return events

class XYZ_Validator(object):
    def __call__(self, form, field):
        if not "{x}" in field.data or not "{y}" in field.data or not "{z}" in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")

class LessThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError("Value must be less than or equal to %s" % self.comp_value_field_name)

class GreaterThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError("Value must be greater than or equal to %s" % self.comp_value_field_name)

class YearPerEpochValidator(object):
    def __init__(self, epoch_id_field_name):
        self.epoch_field = epoch_id_field_name

    def __call__(self, form, field):
        epoch_id = form._fields.get(self.epoch_field).data

        ep = Epoch.query.filter_by(id=epoch_id).first()

        if ep == None:
            raise ValidationError("Unknown epoch.")

        if ep.years != 0 and (field.data < 1 or field.data > ep.years):
            raise ValidationError("Year " + field.data + " is invalid for this epoch.")

class DayPerMonthValidator(object):
    def __init__(self, month_id_field_name):
        self.month_field = month_id_field_name

    def __call__(self, form, field):
        month_id = form._fields.get(self.month_field).data

        mo = Month.query.filter_by(id=month_id).first()

        if mo == None:
            raise ValidationError("Unknown month.")

        if field.data < 1 or field.data > mo.days:
            raise ValidationError("Day " + field.data + " is invalid for this month.")