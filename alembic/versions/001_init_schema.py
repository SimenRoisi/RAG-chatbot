"""init schema

Revision ID: 001_init_schema
Revises: 
Create Date: 2026-01-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_init_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('api_key_hash', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('api_key_hash', name='uq_users_api_key_hash'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # ApiUsage
    op.create_table('api_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_key_hash', sa.String(length=128), nullable=False),
        sa.Column('endpoint', sa.String(length=128), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_api_usage'))
    )
    op.create_index(op.f('ix_api_usage_api_key_hash'), 'api_usage', ['api_key_hash'], unique=False)
    op.create_index(op.f('ix_api_usage_timestamp'), 'api_usage', ['timestamp'], unique=False)
    op.create_index('ix_api_usage_key_hash_endpoint_time', 'api_usage', ['api_key_hash', 'endpoint', 'timestamp'], unique=False)

    # Documents
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_documents_owner_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_documents'))
    )
    op.create_index(op.f('ix_documents_created_at'), 'documents', ['created_at'], unique=False)
    op.create_index(op.f('ix_documents_owner_id'), 'documents', ['owner_id'], unique=False)

    # DocumentChunks
    op.create_table('document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name=op.f('fk_document_chunks_document_id_documents'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_document_chunks'))
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_document_chunks_document_id'), table_name='document_chunks')
    op.drop_table('document_chunks')
    op.drop_index(op.f('ix_documents_owner_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_created_at'), table_name='documents')
    op.drop_table('documents')
    op.drop_index('ix_api_usage_key_hash_endpoint_time', table_name='api_usage')
    op.drop_index(op.f('ix_api_usage_timestamp'), table_name='api_usage')
    op.drop_index(op.f('ix_api_usage_api_key_hash'), table_name='api_usage')
    op.drop_table('api_usage')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')
    op.execute("DROP EXTENSION IF EXISTS vector")
