"""Add columns to claim table and alter existing columns

Revision ID: 3b95192ab1c7
Revises: bd5f1bbda402
Create Date: 2024-07-22 05:42:18.568097

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '3b95192ab1c7'
down_revision = 'bd5f1bbda402'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    with op.batch_alter_table('claim', schema=None) as batch_op:
        if 'claim_item_id_fkey' in [fk['name'] for fk in inspector.get_foreign_keys('claim')]:
            batch_op.drop_constraint('claim_item_id_fkey', type_='foreignkey')
        batch_op.add_column(sa.Column('found_item_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('claim_reason', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('date_initiated', sa.DateTime(), nullable=False))
        batch_op.create_foreign_key('fk_claim_found_item', 'found_report', ['found_item_id'], ['id'])
        batch_op.drop_column('date_claimed')
        batch_op.drop_column('description')
        batch_op.drop_column('item_id')

    with op.batch_alter_table('found_report', schema=None) as batch_op:
        batch_op.alter_column('date_reported',
               existing_type=sa.DATETIME(),
               type_=sa.Date(),
               existing_nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)

    with op.batch_alter_table('lost_report', schema=None) as batch_op:
        batch_op.alter_column('date_reported',
               existing_type=sa.DATETIME(),
               type_=sa.Date(),
               existing_nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)

def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    with op.batch_alter_table('lost_report', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('date_reported',
               existing_type=sa.Date(),
               type_=sa.DATETIME(),
               existing_nullable=False)

    with op.batch_alter_table('found_report', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('date_reported',
               existing_type=sa.Date(),
               type_=sa.DATETIME(),
               existing_nullable=False)

    with op.batch_alter_table('claim', schema=None) as batch_op:
        if 'fk_claim_found_item' in [fk['name'] for fk in inspector.get_foreign_keys('claim')]:
            batch_op.drop_constraint('fk_claim_found_item', type_='foreignkey')
        batch_op.add_column(sa.Column('item_id', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('description', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('date_claimed', sa.DATETIME(), nullable=False))
        batch_op.create_foreign_key('claim_item_id_fkey', 'item', ['item_id'], ['id'])
        batch_op.drop_column('date_initiated')
        batch_op.drop_column('claim_reason')
        batch_op.drop_column('found_item_id')



