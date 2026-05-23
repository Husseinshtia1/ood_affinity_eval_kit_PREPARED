from alembic import op
import sqlalchemy as sa

revision='0002_audit_logs'
down_revision='0001_initial_schema'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('actor_user_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=True),
        sa.Column('organization_id',sa.Integer(),sa.ForeignKey('organizations.id'),nullable=True),
        sa.Column('action',sa.String(100),nullable=False),
        sa.Column('resource_type',sa.String(100),nullable=False),
        sa.Column('resource_id',sa.String(255),nullable=True),
        sa.Column('metadata_json',sa.JSON(),nullable=True),
        sa.Column('created_at',sa.DateTime(timezone=True))
    )


def downgrade():
    op.drop_table('audit_logs')
