"""update document model for file uploads

Revision ID: de761d78c1de
Revises: b15f35c9a49d
Create Date: 2024-02-22 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'de761d78c1de'
down_revision: Union[str, None] = 'b15f35c9a49d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем старую таблицу
    op.drop_table('documents')
    
    # Создаем новую таблицу
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('system_filename', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем индексы
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    op.create_index(op.f('ix_documents_system_filename'), 'documents', ['system_filename'], unique=True)


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index(op.f('ix_documents_system_filename'), table_name='documents')
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    
    # Удаляем таблицу
    op.drop_table('documents')
    
    # Восстанавливаем старую структуру
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
