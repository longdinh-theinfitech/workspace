"""Update user

Revision ID: ca1b05c4912e
Revises: c51958e245e4
Create Date: 2024-12-29 16:28:09.246049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca1b05c4912e'
down_revision: Union[str, None] = 'c51958e245e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'url')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('url', sa.VARCHAR(length=255), autoincrement=False, nullable=True, comment='URL'))
    # ### end Alembic commands ###
