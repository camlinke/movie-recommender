"""empty message

Revision ID: 107c07702c66
Revises: 1a167de09a80
Create Date: 2015-08-20 16:37:34.781910

"""

# revision identifiers, used by Alembic.
revision = '107c07702c66'
down_revision = '1a167de09a80'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('imdb_id', sa.String(), nullable=True))
    op.add_column('movies', sa.Column('tmdb_id', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movies', 'tmdb_id')
    op.drop_column('movies', 'imdb_id')
    ### end Alembic commands ###
