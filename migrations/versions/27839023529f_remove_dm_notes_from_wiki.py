"""remove dm notes from wiki

Revision ID: 27839023529f
Revises: b0ecdd58f5f8
Create Date: 2020-05-24 10:57:46.338303

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '27839023529f'
down_revision = 'b0ecdd58f5f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wiki_entries', schema=None) as batch_op:
        batch_op.drop_column('dm_content')

    with op.batch_alter_table('wiki_settings', schema=None) as batch_op:
        batch_op.drop_column('default_visible')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wiki_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('default_visible', sa.BOOLEAN(), nullable=True))

    with op.batch_alter_table('wiki_entries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dm_content', sa.TEXT(), nullable=True))

    # ### end Alembic commands ###
