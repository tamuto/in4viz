"""draw.io形式での出力例

このサンプルを実行するには:
    cd /kira/in4viz.feature-reset
    PYTHONPATH=packages:$PYTHONPATH python3 examples/drawio_example.py
"""

import sys
from pathlib import Path

# パッケージへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages'))

from in4viz.backends.drawio import DrawioERDiagram
from in4viz import Table, Column, LineType, Cardinality


def main():
    """draw.io形式でER図を作成"""
    print("Creating ER diagram in draw.io format...")

    # draw.ioバックエンドを直接使用
    diagram = DrawioERDiagram(default_line_type=LineType.CRANK)

    # 顧客テーブル
    customers = Table(
        name='customers',
        logical_name='顧客',
        columns=[
            Column('id', '顧客ID', 'INT', primary_key=True, nullable=False),
            Column('company_name', '会社名', 'VARCHAR(200)', nullable=False),
            Column('contact_name', '担当者名', 'VARCHAR(100)', nullable=False),
            Column('email', 'メールアドレス', 'VARCHAR(255)', nullable=False, index=True),
            Column('phone', '電話番号', 'VARCHAR(20)'),
            Column('address', '住所', 'TEXT'),
        ]
    )

    # 注文テーブル
    orders = Table(
        name='orders',
        logical_name='注文',
        columns=[
            Column('id', '注文ID', 'INT', primary_key=True, nullable=False),
            Column('customer_id', '顧客ID', 'INT', nullable=False, foreign_key=True, index=True),
            Column('order_date', '注文日', 'DATE', nullable=False),
            Column('total_amount', '合計金額', 'DECIMAL(10,2)', nullable=False),
            Column('status', 'ステータス', 'VARCHAR(20)', nullable=False),
            Column('notes', '備考', 'TEXT'),
        ]
    )

    # 商品テーブル
    products = Table(
        name='products',
        logical_name='商品',
        columns=[
            Column('id', '商品ID', 'INT', primary_key=True, nullable=False),
            Column('name', '商品名', 'VARCHAR(200)', nullable=False),
            Column('description', '商品説明', 'TEXT'),
            Column('price', '単価', 'DECIMAL(10,2)', nullable=False),
            Column('stock', '在庫数', 'INT', nullable=False),
        ]
    )

    # 注文明細テーブル
    order_items = Table(
        name='order_items',
        logical_name='注文明細',
        columns=[
            Column('order_id', '注文ID', 'INT', primary_key=True, nullable=False, foreign_key=True),
            Column('product_id', '商品ID', 'INT', primary_key=True, nullable=False, foreign_key=True),
            Column('quantity', '数量', 'INT', nullable=False),
            Column('unit_price', '単価', 'DECIMAL(10,2)', nullable=False),
        ]
    )

    # テーブルを追加
    diagram.add_table(customers)
    diagram.add_table(orders)
    diagram.add_table(products)
    diagram.add_table(order_items)

    # リレーションシップを追加（クランク線で）
    diagram.add_edge(
        'orders', 'customers',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'order_items', 'orders',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'order_items', 'products',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )

    # draw.ioファイルとして保存
    output_path = Path(__file__).parent / 'drawio_example.drawio'
    diagram.save_drawio(str(output_path))

    print(f"✓ draw.io diagram saved to: {output_path}")
    print(f"  Open it in draw.io (https://app.diagrams.net/) to view and edit")


if __name__ == '__main__':
    main()
