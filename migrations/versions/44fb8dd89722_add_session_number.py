"""add session_number

Revision ID: 44fb8dd89722
Revises: 4ca4f5fb810d
Create Date: 2020-04-25 15:59:05.943076

"""
from alembic import op
import sqlalchemy as sa
from app import db
from app.campaign.models import Campaign
from app.session.helpers import recalc_session_numbers


# revision identifiers, used by Alembic.
revision = '44fb8dd89722'
down_revision = '4ca4f5fb810d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_number', sa.Integer(), nullable=True))

    # ### end Alembic commands ###

    campaigns = Campaign.query.all()
    for campaign in campaigns:
        print("calculating session numbers for campaign {}".format(campaign.name))
        recalc_session_numbers(campaign, db)

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_column('session_number')

    # ### end Alembic commands ###
