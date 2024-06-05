"""creating-database

Revision ID: 15649f7ae58b
Revises: 
Create Date: 2024-06-05 10:44:28.341540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15649f7ae58b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('bank_payment_id', sa.String(length=200), nullable=True),
    sa.Column('qr_code', sa.UnicodeText(), nullable=True),
    sa.Column('expiration_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    # ### end Alembic commands ###
