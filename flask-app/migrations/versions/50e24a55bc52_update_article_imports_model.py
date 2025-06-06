"""Update article_imports model

Revision ID: 50e24a55bc52
Revises: aac1abd4f9a3
Create Date: 2025-02-19 14:03:04.975327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50e24a55bc52'
down_revision = 'aac1abd4f9a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article_imports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('corrected', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article_imports', schema=None) as batch_op:
        batch_op.drop_column('corrected')

    # ### end Alembic commands ###
