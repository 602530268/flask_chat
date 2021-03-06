"""empty message

Revision ID: 2623add59629
Revises: 8fb19b6e9b30
Create Date: 2018-11-07 18:26:41.652432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2623add59629'
down_revision = '8fb19b6e9b30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('friend_circle',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('weather', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('friend_circle')
    # ### end Alembic commands ###
