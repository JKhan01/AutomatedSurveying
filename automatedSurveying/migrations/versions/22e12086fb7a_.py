"""empty message

Revision ID: 22e12086fb7a
Revises: 
Create Date: 2020-11-02 08:37:17.356591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22e12086fb7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('imagesdetails',
    sa.Column('projectid', sa.Integer(), nullable=False),
    sa.Column('imagename', sa.String(length=20), nullable=False),
    sa.Column('height', sa.Numeric(), nullable=False),
    sa.PrimaryKeyConstraint('imagename')
    )
    op.create_table('projectdetails',
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('projectid', sa.Integer(), nullable=False),
    sa.Column('projectname', sa.String(length=100), nullable=False),
    sa.Column('extent', sa.Numeric(), nullable=False),
    sa.PrimaryKeyConstraint('projectid')
    )
    op.create_table('userdetails',
    sa.Column('name', sa.String(length=15), nullable=False),
    sa.Column('emailid', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('emailid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userdetails')
    op.drop_table('projectdetails')
    op.drop_table('imagesdetails')
    # ### end Alembic commands ###