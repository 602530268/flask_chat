"""empty message

Revision ID: 549de8a2d5f6
Revises: 
Create Date: 2018-11-06 18:13:02.811157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '549de8a2d5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('account', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=20), nullable=False),
    sa.Column('telephone', sa.String(length=11), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('username', sa.String(length=20), nullable=True),
    sa.Column('intro', sa.Text(), nullable=True),
    sa.Column('head_img_url', sa.String(length=255), nullable=True),
    sa.Column('sex', sa.Integer(), nullable=True),
    sa.Column('net_status', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
