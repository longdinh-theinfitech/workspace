"""Add api usage

Revision ID: a19396539678
Revises: bb8a2e0fddeb
Create Date: 2024-12-30 17:37:06.846596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a19396539678'
down_revision: Union[str, None] = 'bb8a2e0fddeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_usage',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('account_id', sa.BIGINT(), nullable=True),
    sa.Column('api_name', sa.Text(), nullable=True),
    sa.Column('request_count', sa.Integer(), nullable=True),
    sa.Column('is_banned', sa.Boolean(), nullable=True),
    sa.Column('last_reset', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='api_usage_account_id_fkey'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_id', 'api_name', name='api_usage_account_id_api_name_key')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('api_usage')
    # ### end Alembic commands ###
