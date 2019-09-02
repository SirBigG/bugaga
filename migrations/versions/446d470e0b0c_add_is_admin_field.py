"""add is_admin field

Revision ID: 446d470e0b0c
Revises: 4674009f0de3
Create Date: 2019-09-02 13:55:05.030211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '446d470e0b0c'
down_revision = '4674009f0de3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tusers',
                  sa.Column('is_admin', sa.Boolean(), default=False))


def downgrade():
    op.drop_column('tusers', "is_admin")
