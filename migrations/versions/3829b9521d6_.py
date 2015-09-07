"""empty message

Revision ID: 3829b9521d6
Revises: None
Create Date: 2015-09-07 02:58:37.500914

"""

# revision identifiers, used by Alembic.
revision = '3829b9521d6'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('genre_name', sa.String(), nullable=True),
    sa.Column('movie_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('movie_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('imdb_id', sa.String(), nullable=True),
    sa.Column('tmdb_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ratings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('movie_lense_user_id', sa.String(), nullable=True),
    sa.Column('movie_id', sa.String(), nullable=False),
    sa.Column('rating', sa.String(), nullable=False),
    sa.Column('timestamp', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ratings_movie_id'), 'ratings', ['movie_id'], unique=False)
    op.create_index(op.f('ix_ratings_movie_lense_user_id'), 'ratings', ['movie_lense_user_id'], unique=False)
    op.create_index(op.f('ix_ratings_user_id'), 'ratings', ['user_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('pw_hash', sa.String(), nullable=True),
    sa.Column('recommendations', postgresql.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_index(op.f('ix_ratings_user_id'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_movie_lense_user_id'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_movie_id'), table_name='ratings')
    op.drop_table('ratings')
    op.drop_table('movies')
    op.drop_table('genres')
    ### end Alembic commands ###