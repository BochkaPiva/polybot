"""add text version

Revision ID: add_text_version
Revises: 
Create Date: 2024-03-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_text_version'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем колонку text_version
    op.add_column('documents', sa.Column('text_version', sa.Integer(), nullable=False, server_default='1'))

def downgrade():
    # Удаляем колонку text_version
    op.drop_column('documents', 'text_version') 