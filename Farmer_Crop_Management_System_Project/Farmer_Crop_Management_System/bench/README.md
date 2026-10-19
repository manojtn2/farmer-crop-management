# Quick instructions to enable SQL logging and run the benchmark

1. Enable SQL logging (temporary, for profiling)

   - Option A (recommended for Flask-SQLAlchemy): in a Python shell or a local debug file:

       from sql_logging import enable_sql_logging
       enable_sql_logging('INFO')

   - Option B: set SQLAlchemy echo in config.py (not recommended in production):

       SQLALCHEMY_ECHO = True

2. Run the benchmark script against your running dev server

    pip install requests
    python Farmer_Crop_Management_System_Project/Farmer_Crop_Management_System/bench/benchmark.py http://127.0.0.1:5000 --runs 20

3. Apply the Alembic migration

   - If you use Alembic already, copy the file migrations/versions/0001_add_indexes.py into your alembic versions directory and run:

       alembic upgrade head

   - If you don't use Alembic, run the SQL below against your database (psql/mysql client) to create the indexes manually:

       CREATE INDEX ix_crop_user_id ON crop(user_id);
       CREATE INDEX ix_activity_crop_id ON activity(crop_id);
       CREATE INDEX ix_expense_crop_id ON expense(crop_id);
       CREATE INDEX ix_harvest_crop_id ON harvest(crop_id);
