"""Add a column twitter id

Revision ID: c51958e245e4
Revises: 5a6e79de2a8c
Create Date: 2024-12-29 16:24:58.965157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c51958e245e4'
down_revision: Union[str, None] = '5a6e79de2a8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('twitter_id', sa.String(length=255), nullable=False, comment='Twitter ID'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'twitter_id')
    # ### end Alembic commands ###
