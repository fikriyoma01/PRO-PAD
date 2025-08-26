from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('param_registry',
        sa.Column('param_key', sa.String(), primary_key=True),
        sa.Column('value_num', sa.Numeric()),
        sa.Column('value_text', sa.Text()),
        sa.Column('unit', sa.String()),
        sa.Column('min_val', sa.Numeric()),
        sa.Column('max_val', sa.Numeric()),
        sa.Column('source', sa.String()),
        sa.Column('owner', sa.String()),
        sa.Column('effective_from', sa.Date()),
        sa.Column('effective_to', sa.Date()),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('updated_by', sa.String()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table('forecast_run',
        sa.Column('run_id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.Column('horizon_months', sa.Integer(), nullable=False)
    )
    op.create_table('forecast_result',
        sa.Column('run_id', sa.String(), sa.ForeignKey('forecast_run.run_id'), primary_key=True),
        sa.Column('periode', sa.Date(), primary_key=True),
        sa.Column('jenis_pajak', sa.String(), primary_key=True),
        sa.Column('nilai', sa.Numeric(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False)
    )
    op.create_table('scenario',
        sa.Column('scenario_id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('overrides_json', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('active', sa.Boolean(), server_default='true')
    )

def downgrade():
    op.drop_table('scenario')
    op.drop_table('forecast_result')
    op.drop_table('forecast_run')
    op.drop_table('param_registry')
