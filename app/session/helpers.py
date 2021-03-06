from app.character.models import Character
from app.party.models import Party
from app.session.models import Session
from sqlalchemy import and_


# generate choices for session participant SelectField (multi-select)
# tuples are nested by party (=optgroup)
def gen_participant_choices(ensure=None):
    choices = []

    parties = Party.query.all()

    for party in parties:
        if len(party.members) == 0:
            continue

        members = []

        for member in party.members:
            if member.is_visible or (ensure is not None and member in ensure):
                members.append((member.id, f"{member.name} ({member.player.username})"))

        if len(members) > 0:
            choices.append((party.name, members))

    # this used to be filter(Character.parties == None), which worked but is but not PEP compliant
    # with filter(Character.parties is None) it didn't work
    # so we use a negated any() to check for empty collections
    # see https://docs.sqlalchemy.org/en/14/orm/internals.html#sqlalchemy.orm.RelationshipProperty.Comparator.any
    # side note: this was the first bug found by unit tests :-)
    no_party_chars = Character.query.filter(~Character.parties.any()).all()

    if len(no_party_chars) > 0:
        members = []

        for char in no_party_chars:
            if char.is_visible or (ensure is not None and char in ensure):
                members.append((char.id, f"{char.name} ({char.player.username})"))

        if len(members) > 0:
            choices.append(("No Party", members))

    return choices


# get the previous session for a specified campaign code (if applicable)
def get_previous_session(session):
    q = Session.query.filter(and_(Session.campaign_id == session.campaign_id, Session.date < session.date)) \
        .order_by(Session.date.desc()).first()
    return q


# get the next session for a specified campaign (if applicable)
def get_next_session(session):
    q = Session.query.filter(and_(Session.campaign_id == session.campaign_id, Session.date > session.date)) \
        .order_by(Session.date.asc()).first()
    return q


def recalc_session_numbers(campaign, db):
    sessions = Session.query.filter(Session.campaign_id == campaign.id).order_by(Session.date.asc()).all()
    count = 1

    for session in sessions:
        session.session_number = count
        count += 1

    db.session.commit()
