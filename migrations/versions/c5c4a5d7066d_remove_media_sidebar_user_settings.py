"""remove media sidebar user settings

Revision ID: c5c4a5d7066d
Revises: 27839023529f
Create Date: 2020-05-24 15:57:00.034483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5c4a5d7066d'
down_revision = '27839023529f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('use_direct_links')
        batch_op.drop_column('use_embedded_images')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('use_embedded_images', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('use_direct_links', sa.BOOLEAN(), nullable=True))

    # ### end Alembic commands ###