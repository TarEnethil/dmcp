"""consolidate user markdown style options

Revision ID: f5ed086662b7
Revises: e47511507b2a
Create Date: 2019-05-05 13:51:34.983896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5ed086662b7'
down_revision = 'e47511507b2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('markdown_phb_style', sa.Boolean(), nullable=True))
        batch_op.drop_column('phb_character')
        batch_op.drop_column('phb_session')
        batch_op.drop_column('phb_wiki')
        batch_op.drop_column('phb_party')
        batch_op.drop_column('phb_calendar')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phb_calendar', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('phb_party', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('phb_wiki', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('phb_session', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('phb_character', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('markdown_phb_style')

    # ### end Alembic commands ###
