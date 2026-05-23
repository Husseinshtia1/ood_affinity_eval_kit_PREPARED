from alembic import op
import sqlalchemy as sa

revision='0001_initial_schema'
down_revision=None
branch_labels=None
depends_on=None


def upgrade():
    op.create_table(
        'organizations',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('name',sa.String(255),unique=True,nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True))
    )

    op.create_table(
        'users',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('email',sa.String(255),unique=True,nullable=False),
        sa.Column('hashed_password',sa.String(255),nullable=False),
        sa.Column('role',sa.String(50)),
        sa.Column('organization_id',sa.Integer(),sa.ForeignKey('organizations.id')),
        sa.Column('created_at',sa.DateTime(timezone=True))
    )

    op.create_table(
        'evaluations',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('job_id',sa.String(255),unique=True,nullable=False),
        sa.Column('owner_id',sa.Integer(),sa.ForeignKey('users.id')),
        sa.Column('status',sa.String(50),nullable=False)
    )


def downgrade():
    op.drop_table('evaluations')
    op.drop_table('users')
    op.drop_table('organizations')
