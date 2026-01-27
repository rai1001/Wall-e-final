"""add meeting_audios"""

from alembic import op
import sqlalchemy as sa
from app.models import MeetingStatus

# revision identifiers, used by Alembic.
revision = "202601271900"
down_revision = "202601271640"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meeting_audios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("status", sa.Enum(MeetingStatus), nullable=False, server_default=MeetingStatus.pending.value),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("action_items", sa.JSON(), nullable=True),
        sa.Column("error", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("meeting_audios")
