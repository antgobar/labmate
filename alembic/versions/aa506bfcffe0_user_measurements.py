"""user_measurements

Revision ID: aa506bfcffe0
Revises: ff34750b3fbc
Create Date: 2024-08-30 12:47:05.695251

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aa506bfcffe0"
down_revision: Union[str, None] = "ff34750b3fbc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("measurements", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("measurements", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "measurements", "users", ["user_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "measurements", type_="foreignkey")
    op.drop_column("measurements", "user_id")
    op.drop_column("measurements", "updated_at")
    # ### end Alembic commands ###