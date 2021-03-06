"""Add oauth scopes column

Revision ID: 125cf4a92c42
Revises: 29da022b74a8
Create Date: 2017-04-16 11:33:52.288486

"""

# revision identifiers, used by Alembic.
revision = '125cf4a92c42'
down_revision = '29da022b74a8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('oauth_token_scopes', sa.String(), nullable=False, server_default=''))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'oauth_token_scopes')
    # ### end Alembic commands ###
