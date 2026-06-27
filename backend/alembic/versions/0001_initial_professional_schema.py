"""initial professional schema

Revision ID: 0001_initial_professional_schema
Revises:
Create Date: 2026-06-27
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_professional_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users', sa.Column('id',sa.String(),primary_key=True), sa.Column('email',sa.String(220),nullable=False), sa.Column('name',sa.String(160),nullable=False), sa.Column('role',sa.String(32),nullable=False), sa.Column('password_hash',sa.String(300),nullable=False), sa.Column('is_active',sa.Boolean(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_index('ix_users_email','users',['email'],unique=True)
    op.create_table('api_keys', sa.Column('id',sa.String(),primary_key=True), sa.Column('name',sa.String(160),nullable=False), sa.Column('key_prefix',sa.String(24),nullable=False), sa.Column('key_hash',sa.String(128),nullable=False), sa.Column('scoped_role',sa.String(32),nullable=False), sa.Column('owner_user_id',sa.String(),nullable=True), sa.Column('is_active',sa.Boolean(),nullable=False), sa.Column('last_used_at',sa.DateTime(timezone=True),nullable=True), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True), sa.Column('revoked_at',sa.DateTime(timezone=True),nullable=True), sa.Column('notes',sa.Text(),nullable=True))
    op.create_index('ix_api_keys_key_hash','api_keys',['key_hash'],unique=True)
    op.create_table('targets', sa.Column('id',sa.String(),primary_key=True), sa.Column('name',sa.String(160),nullable=False), sa.Column('type',sa.String(80),nullable=False), sa.Column('endpoint_url',sa.String(500),nullable=True), sa.Column('safe_mode',sa.Boolean(),nullable=False), sa.Column('config_json',sa.Text(),nullable=True), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_table('scans', sa.Column('id',sa.String(),primary_key=True), sa.Column('target_id',sa.String(),nullable=False), sa.Column('status',sa.String(32),nullable=False), sa.Column('selected_packs_json',sa.Text(),nullable=True), sa.Column('options_json',sa.Text(),nullable=True), sa.Column('total_tests',sa.Integer(),nullable=False), sa.Column('failed_tests',sa.Integer(),nullable=False), sa.Column('passed_tests',sa.Integer(),nullable=False), sa.Column('risk_score',sa.Float(),nullable=False), sa.Column('job_id',sa.String(),nullable=True), sa.Column('progress',sa.Integer(),nullable=False), sa.Column('current_test',sa.String(220),nullable=True), sa.Column('error_message',sa.Text(),nullable=True), sa.Column('cancelled_at',sa.DateTime(timezone=True),nullable=True), sa.Column('started_at',sa.DateTime(timezone=True),nullable=True), sa.Column('completed_at',sa.DateTime(timezone=True),nullable=True), sa.Column('failed_at',sa.DateTime(timezone=True),nullable=True), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_index('ix_scans_target_id','scans',['target_id'])
    op.create_table('findings', sa.Column('id',sa.String(),primary_key=True), sa.Column('scan_id',sa.String(),nullable=False), sa.Column('attack_pack_id',sa.String(160),nullable=True), sa.Column('test_id',sa.String(160),nullable=True), sa.Column('test_name',sa.String(300),nullable=True), sa.Column('prompt',sa.Text(),nullable=True), sa.Column('response',sa.Text(),nullable=True), sa.Column('detector_name',sa.String(160),nullable=True), sa.Column('passed',sa.Boolean(),nullable=False), sa.Column('severity',sa.String(32),nullable=False), sa.Column('risk_score',sa.Float(),nullable=False), sa.Column('category',sa.String(220),nullable=True), sa.Column('mitre_tactic',sa.String(220),nullable=True), sa.Column('confidence',sa.Float(),nullable=False), sa.Column('evidence',sa.Text(),nullable=True), sa.Column('mitigation',sa.Text(),nullable=True), sa.Column('latency_ms',sa.Integer(),nullable=False), sa.Column('token_estimate',sa.Integer(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_index('ix_findings_scan_id','findings',['scan_id'])
    op.create_table('reports', sa.Column('id',sa.String(),primary_key=True), sa.Column('scan_id',sa.String(),nullable=False), sa.Column('format',sa.String(32),nullable=False), sa.Column('path',sa.String(800),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_table('provider_configs', sa.Column('id',sa.String(),primary_key=True), sa.Column('provider',sa.String(80),nullable=False), sa.Column('model',sa.String(160),nullable=True), sa.Column('is_enabled',sa.Boolean(),nullable=False), sa.Column('safe_config_json',sa.Text(),nullable=True), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_table('audit_logs', sa.Column('id',sa.String(),primary_key=True), sa.Column('actor_user_id',sa.String(),nullable=True), sa.Column('actor_email',sa.String(220),nullable=True), sa.Column('action',sa.String(160),nullable=False), sa.Column('resource_type',sa.String(160),nullable=True), sa.Column('resource_id',sa.String(160),nullable=True), sa.Column('status',sa.String(32),nullable=False), sa.Column('detail_json',sa.Text(),nullable=True), sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))

def downgrade():
    for table in ['audit_logs','provider_configs','reports','findings','scans','targets','api_keys','users']:
        op.drop_table(table)
