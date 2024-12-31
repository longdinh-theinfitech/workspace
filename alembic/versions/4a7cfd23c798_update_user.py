"""Update user

Revision ID: 4a7cfd23c798
Revises: ca1b05c4912e
Create Date: 2024-12-29 16:31:02.475172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a7cfd23c798'
down_revision: Union[str, None] = 'ca1b05c4912e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'favourites_count')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('favourites_count', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
