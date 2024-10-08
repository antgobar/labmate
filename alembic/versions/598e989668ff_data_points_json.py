"""data points json

Revision ID: 598e989668ff
Revises: ff2513834728
Create Date: 2024-08-24 22:20:31.524724

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "598e989668ff"
down_revision: Union[str, None] = "ff2513834728"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("measurements", sa.Column("data_points", sa.JSON(), nullable=True))
    op.drop_column("measurements", "magnitude")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "measurements",
        sa.Column(
            "magnitude",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("measurements", "data_points")
    # ### end Alembic commands ###
