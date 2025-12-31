"""in4viz ライブラリの基本的な使用例

このサンプルを実行するには:
    cd /kira/in4viz.feature-reset
    PYTHONPATH=packages:$PYTHONPATH python3 examples/basic_usage.py
"""

import sys
from pathlib import Path

# パッケージへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages'))

from in4viz import ERDiagram, Table, Column, LineType, Cardinality


def create_example_tables():
    """サンプルテーブルを作成"""
    # ユーザーテーブル
    users_table = Table(
        name='users',
        logical_name='ユーザー',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('name', '名前', 'VARCHAR(100)', nullable=False),
            Column('email', 'メールアドレス', 'VARCHAR(255)', nullable=False, index=True),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False),
        ]
    )

    # 投稿テーブル
    posts_table = Table(
        name='posts',
        logical_name='投稿',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('user_id', 'ユーザーID', 'INT', nullable=False, foreign_key=True, index=True),
            Column('title', 'タイトル', 'VARCHAR(200)', nullable=False),
            Column('content', '本文', 'TEXT'),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False),
        ]
    )

    # カテゴリテーブル
    categories_table = Table(
        name='categories',
        logical_name='カテゴリ',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True, nullable=False),
            Column('name', 'カテゴリ名', 'VARCHAR(100)', nullable=False),
            Column('description', '説明', 'TEXT'),
        ]
    )

    # 投稿カテゴリ中間テーブル
    post_categories_table = Table(
        name='post_categories',
        logical_name='投稿カテゴリ',
        columns=[
            Column('post_id', '投稿ID', 'INT', primary_key=True, nullable=False, foreign_key=True),
            Column('category_id', 'カテゴリID', 'INT', primary_key=True, nullable=False, foreign_key=True),
        ]
    )

    return users_table, posts_table, categories_table, post_categories_table


def create_svg_diagram():
    """SVG形式のER図を作成"""
    print("Creating SVG diagram...")

    # ER図を作成（SVGバックエンド）
    diagram = ERDiagram(backend='svg', default_line_type=LineType.CRANK)

    # テーブルを作成
    users, posts, categories, post_categories = create_example_tables()

    # テーブルを追加
    diagram.add_table(users)
    diagram.add_table(posts)
    diagram.add_table(categories)
    diagram.add_table(post_categories)

    # FK関係を追加
    diagram.add_edge(
        'posts', 'users',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'post_categories', 'posts',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'post_categories', 'categories',
        line_type=LineType.CRANK,
        cardinality=Cardinality(from_side='*', to_side='1')
    )

    # SVGファイルとして保存
    output_path = Path(__file__).parent / 'basic_usage.svg'
    diagram.save(str(output_path))
    print(f"SVG diagram saved to: {output_path}")


def create_drawio_diagram():
    """draw.io形式のER図を作成"""
    print("Creating draw.io diagram...")

    # ER図を作成（draw.ioバックエンド）
    diagram = ERDiagram(backend='drawio', default_line_type=LineType.STRAIGHT)

    # テーブルを作成
    users, posts, categories, post_categories = create_example_tables()

    # テーブルを追加
    diagram.add_table(users)
    diagram.add_table(posts)
    diagram.add_table(categories)
    diagram.add_table(post_categories)

    # FK関係を追加
    diagram.add_edge(
        'posts', 'users',
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'post_categories', 'posts',
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'post_categories', 'categories',
        cardinality=Cardinality(from_side='*', to_side='1')
    )

    # draw.ioファイルとして保存
    output_path = Path(__file__).parent / 'basic_usage.drawio'
    diagram.save(str(output_path))
    print(f"draw.io diagram saved to: {output_path}")


def main():
    """メイン関数"""
    print("in4viz Example - ER Diagram Generator")
    print("=" * 50)

    # SVG形式で出力
    create_svg_diagram()
    print()

    # draw.io形式で出力
    create_drawio_diagram()
    print()

    print("=" * 50)
    print("Done! Both diagrams have been created successfully.")
    print("- basic_usage.svg (can be opened in any browser)")
    print("- basic_usage.drawio (can be opened in draw.io)")


if __name__ == '__main__':
    main()
