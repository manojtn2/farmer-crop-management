"""Alembic migration: add indexes to speed up queries on foreign key columns.

This file follows Alembic's migration script format. If your project uses Alembic, place this
file under migrations/versions/ and run `alembic upgrade head` after configuring alembic.ini.
If you don't use Alembic, you can run the SQL statements inside upgrade() manually against
your database.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes on foreign key columns used in filters: Crop.user_id and *_crop_id
    op.create_index('ix_crop_user_id', 'crop', ['user_id'])
    op.create_index('ix_activity_crop_id', 'activity', ['crop_id'])
    op.create_index('ix_expense_crop_id', 'expense', ['crop_id'])
    op.create_index('ix_harvest_crop_id', 'harvest', ['crop_id'])


def downgrade():
    op.drop_index('ix_harvest_crop_id', table_name='harvest')
    op.drop_index('ix_expense_crop_id', table_name='expense')
    op.drop_index('ix_activity_crop_id', table_name='activity')
    op.drop_index('ix_crop_user_id', table_name='crop')
