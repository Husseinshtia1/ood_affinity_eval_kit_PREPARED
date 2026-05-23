from alembic import op
import sqlalchemy as sa

revision='0004_invitation_delivery_tracking'
down_revision='0003_invitations'


def upgrade():
    op.add_column('invitations', sa.Column('delivery_status', sa.String(50), nullable=False, server_default='pending'))
    op.add_column('invitations', sa.Column('delivery_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('invitations', sa.Column('last_delivery_error', sa.String(500), nullable=True))


def downgrade():
    op.drop_column('invitations','delivery_status')
    op.drop_column('invitations','delivery_attempts')
    op.drop_column('invitations','last_delivery_error')