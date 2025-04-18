"""Agregando tabla BranchImage para múltiples imágenes por sucursal

Revision ID: 7fb9c0770641
Revises: bc291f821e5b
Create Date: 2025-03-17 20:44:02.971400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fb9c0770641'
down_revision = 'bc291f821e5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_country_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'countries', ['country_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('users_country_id_fkey', 'countries', ['country_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###
