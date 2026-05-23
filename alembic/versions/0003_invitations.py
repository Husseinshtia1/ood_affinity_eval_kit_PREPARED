from alembic import op
import sqlalchemy as sa

revision='0003_invitations'
down_revision='0002_audit_logs'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table(
        'invitations',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('email',sa.String(255),nullable=False),
        sa.Column('role',sa.String(50),nullable=False),
        sa.Column('token',sa.String(255),nullable=False,unique=True),
        sa.Column('organization_id',sa.Integer(),sa.ForeignKey('organizations.id')),
        sa.Column('invited_by_user_id',sa.Integer(),sa.ForeignKey('users.id')),
        sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('accepted_at',sa.DateTime(timezone=True),nullable=True),
        sa.Column('created_at',sa.DateTime(timezone=True))
    )

def downgrade():
    op.drop_table('invitations')