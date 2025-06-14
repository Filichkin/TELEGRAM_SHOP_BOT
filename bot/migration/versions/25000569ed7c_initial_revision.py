"""Initial revision

Revision ID: 25000569ed7c
Revises: 771a2d604ad6
Create Date: 2025-06-04 10:06:02.469974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25000569ed7c'
down_revision: Union[str, None] = '771a2d604ad6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('expire', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payments', 'expire')
    # ### end Alembic commands ###
