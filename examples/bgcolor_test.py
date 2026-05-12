"""in4viz 背景色とグラデーション機能のテスト

このサンプルを実行するには:
    cd /kira/in4viz.feature-reset
    python3 examples/bgcolor_test.py
"""

import sys
from pathlib import Path

# パッケージへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages' / 'in4viz' / 'src'))

from in4viz import Table, Column, LineType, Cardinality
from in4viz.backends.svg import SVGERDiagram
from in4viz.backends.drawio import DrawioERDiagram


def create_test_tables():
    """背景色テスト用のテーブルを作成"""

    # 1. デフォルト（白背景）のテーブル
    default_table = Table(
        name='default_table',
        logical_name='デフォルト',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('name', '名前', 'VARCHAR(100)', nullable=False),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False),
        ]
    )

    # 2. 単色背景（青色）のテーブル
    blue_table = Table(
        name='blue_table',
        logical_name='単色背景（青）',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('title', 'タイトル', 'VARCHAR(200)', nullable=False),
            Column('content', '内容', 'TEXT'),
        ],
        bgcolor='#CCE5FF',  # 明るい青色
        use_gradient=False
    )

    # 3. グラデーション背景（緑→白）のテーブル
    gradient_table = Table(
        name='gradient_table',
        logical_name='グラデーション（緑→白）',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('category', 'カテゴリ', 'VARCHAR(100)', nullable=False),
            Column('description', '説明', 'TEXT'),
        ],
        bgcolor='#B8E6B8',  # 明るい緑色
        use_gradient=True
    )

    # 4. グラデーション背景（ピンク→白）のテーブル
    pink_gradient_table = Table(
        name='pink_gradient_table',
        logical_name='グラデーション（ピンク→白）',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('tag', 'タグ', 'VARCHAR(50)', nullable=False, index=True),
        ],
        bgcolor='#FFD9E6',  # 明るいピンク色
        use_gradient=True
    )

    return default_table, blue_table, gradient_table, pink_gradient_table


def create_svg_diagram():
    """SVG形式のER図を作成（背景色テスト）"""
    print("Creating SVG diagram with background colors...")

    # ER図を作成（SVGバックエンド）
    diagram = SVGERDiagram(default_line_type=LineType.CRANK)

    # テーブルを作成
    default_table, blue_table, gradient_table, pink_gradient_table = create_test_tables()

    # テーブルを追加
    diagram.add_table(default_table)
    diagram.add_table(blue_table)
    diagram.add_table(gradient_table)
    diagram.add_table(pink_gradient_table)

    # FK関係を追加（視覚的なつながりを作るため）
    diagram.add_edge(
        'blue_table', 'default_table',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'gradient_table', 'blue_table',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )

    # SVGファイルとして保存
    output_path = Path(__file__).parent / 'bgcolor_test.svg'
    diagram.save_svg(str(output_path))
    print(f"SVG diagram saved to: {output_path}")


def create_drawio_diagram():
    """draw.io形式のER図を作成（背景色テスト）"""
    print("Creating draw.io diagram with background colors...")

    # ER図を作成（draw.ioバックエンド）
    diagram = DrawioERDiagram(default_line_type=LineType.STRAIGHT)

    # テーブルを作成
    default_table, blue_table, gradient_table, pink_gradient_table = create_test_tables()

    # テーブルを追加
    diagram.add_table(default_table)
    diagram.add_table(blue_table)
    diagram.add_table(gradient_table)
    diagram.add_table(pink_gradient_table)

    # FK関係を追加
    diagram.add_edge(
        'blue_table', 'default_table',
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'gradient_table', 'blue_table',
        cardinality=Cardinality(from_side='*', to_side='1')
    )

    # draw.ioファイルとして保存
    output_path = Path(__file__).parent / 'bgcolor_test.drawio'
    diagram.save_drawio(str(output_path))
    print(f"draw.io diagram saved to: {output_path}")


def main():
    """メイン関数"""
    print("in4viz Background Color & Gradient Test")
    print("=" * 50)

    # SVG形式で出力
    create_svg_diagram()
    print()

    # draw.io形式で出力
    create_drawio_diagram()
    print()

    print("=" * 50)
    print("Done! Test diagrams have been created successfully.")
    print("- bgcolor_test.svg (can be opened in any browser)")
    print("- bgcolor_test.drawio (can be opened in draw.io)")
    print()
    print("Test patterns:")
    print("  1. Default (white background)")
    print("  2. Solid color (blue background)")
    print("  3. Gradient (green to white)")
    print("  4. Gradient (pink to white)")


if __name__ == '__main__':
    main()
