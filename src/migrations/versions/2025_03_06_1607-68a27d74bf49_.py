"""empty message

Revision ID: 68a27d74bf49
Revises: 29846e26553e
Create Date: 2025-03-06 16:07:07.460605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '68a27d74bf49'
down_revision: Union[str, None] = '29846e26553e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Исходный и новый Enum
old_enum = sa.Enum('IN_QUEUE', 'DIAGNOSTICS', 'DIAGNOSTICS_COMPLETED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED',
                   name='status')
new_enum = sa.Enum('IN_QUEUE', 'DIAGNOSTICS', 'DIAGNOSTICS_COMPLETED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED',
                   'REPAIR_IS_NOT_POSSIBLE', name='status')


def upgrade():
    # 1. Переименовываем существующий тип, чтобы освободить имя 'status'
    op.execute('ALTER TYPE status RENAME TO status_old')

    # 2. Создаем новый тип 'status' с новым значением
    new_enum.create(op.get_bind(), checkfirst=False)

    # 3. Изменяем тип колонки на новый 'status'
    op.alter_column('order', 'status',
                    type_=new_enum,
                    postgresql_using='status::text::status')

    # 4. Удаляем старый тип 'status_old'
    op.execute('DROP TYPE status_old')


def downgrade():
    # 1. Переименовываем новый тип, чтобы освободить имя 'status'
    op.execute('ALTER TYPE status RENAME TO status_new')

    # 2. Создаем старый тип 'status' без нового значения
    old_enum.create(op.get_bind(), checkfirst=False)

    # 3. Изменяем тип колонки на старый 'status'
    op.alter_column('order', 'status',
                    type_=old_enum,
                    postgresql_using='status::text::status')

    # 4. Удаляем новый тип 'status_new'
    op.execute('DROP TYPE status_new')
