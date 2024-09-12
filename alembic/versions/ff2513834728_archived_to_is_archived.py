"""archived to is_archived

Revision ID: ff2513834728
Revises: 1fdcbbb91d46
Create Date: 2024-08-24 15:01:21.007020

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ff2513834728"
down_revision: Union[str, None] = "1fdcbbb91d46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("experiments", sa.Column("is_archived", sa.Boolean(), nullable=True))
    op.drop_column("experiments", "archived")
    op.add_column("lab_samples", sa.Column("is_archived", sa.Boolean(), nullable=True))
    op.drop_column("lab_samples", "archived")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "lab_samples",
        sa.Column("archived", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.drop_column("lab_samples", "is_archived")
    op.add_column(
        "experiments",
        sa.Column(
            "archived",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("experiments", "is_archived")
    # ### end Alembic commands ###