"""experiment has labsamples

Revision ID: 6e1ca1d1e441
Revises: 71c38c37a482
Create Date: 2024-08-18 23:16:48.097806

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e1ca1d1e441"
down_revision: Union[str, None] = "71c38c37a482"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "lab_samples", sa.Column("experiment_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, "lab_samples", "experiments", ["experiment_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "lab_samples", type_="foreignkey")
    op.drop_column("lab_samples", "experiment_id")
    # ### end Alembic commands ###