"""empty message

Revision ID: 4505fc8bddbe
Revises: 310eaf7897af
Create Date: 2015-08-18 15:51:19.673723

"""

# revision identifiers, used by Alembic.
revision = '4505fc8bddbe'
down_revision = '310eaf7897af'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_ratings_user_id'), 'ratings', ['user_id'], unique=False)
    op.drop_column('users', 'ratings')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('ratings', postgresql.JSON(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_ratings_user_id'), table_name='ratings')
    ### end Alembic commands ###
