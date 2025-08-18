#!/usr/bin/env python3

from in4viz import ERDiagram, Table, Column, LineType, Cardinality

def main():
    diagram = ERDiagram()

    # ユーザーテーブル
    users_table = Table(
        name='users',
        logical_name='ユーザー',
        columns=[
            Column('id', 'ユーザーID', 'INT', primary_key=True, nullable=False),
            Column('username', 'ユーザー名', 'VARCHAR(50)', nullable=False, index=True),
            Column('email', 'メールアドレス', 'VARCHAR(100)', nullable=False, index=True),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False)
        ]
    )
    diagram.add_table(users_table)

    # 投稿テーブル
    posts_table = Table(
        name='posts',
        logical_name='投稿',
        columns=[
            Column('id', '投稿ID', 'INT', primary_key=True, nullable=False),
            Column('user_id', 'ユーザーID', 'INT', nullable=False, foreign_key=True, index=True),
            Column('title', 'タイトル', 'VARCHAR(200)', nullable=False, index=True),
            Column('content', '本文', 'TEXT', nullable=True),
            Column('published_at', '公開日時', 'TIMESTAMP', nullable=True)
        ]
    )
    diagram.add_table(posts_table)

    # カテゴリテーブル
    categories_table = Table(
        name='categories',
        logical_name='カテゴリ',
        columns=[
            Column('id', 'カテゴリID', 'INT', primary_key=True, nullable=False),
            Column('name', 'カテゴリ名', 'VARCHAR(100)', nullable=False),
            Column('description', '説明', 'TEXT', nullable=True)
        ]
    )
    diagram.add_table(categories_table)

    # 投稿カテゴリテーブル
    post_categories_table = Table(
        name='post_categories',
        logical_name='投稿カテゴリ',
        columns=[
            Column('post_id', '投稿ID', 'INT', primary_key=True, nullable=False, foreign_key=True),
            Column('category_id', 'カテゴリID', 'INT', primary_key=True, nullable=False, foreign_key=True)
        ]
    )
    diagram.add_table(post_categories_table)

    # ユーザ種別テーブル
    user_types_table = Table(
        name='user_types',
        logical_name='ユーザ種別',
        columns=[
            Column('id', '種別ID', 'INT', primary_key=True, nullable=False),
            Column('type_name', '種別名', 'VARCHAR(50)', nullable=False),
            Column('description', '説明', 'TEXT', nullable=True)
        ]
    )
    diagram.add_table(user_types_table)

    # エッジ（関係線）の追加 - 物理テーブル名を使用（IE記法確認用）
    diagram.add_edge('posts', 'users', LineType.STRAIGHT, Cardinality('*', '1'))  # posts -> users (多対一)
    diagram.add_edge('post_categories', 'posts', LineType.STRAIGHT, Cardinality('0...*', '0'))  # post_categories -> posts (ゼロ以上多数対ゼロ)
    diagram.add_edge('post_categories', 'categories', LineType.STRAIGHT, Cardinality('1', '1...*'))  # post_categories -> categories (一対一以上多数)
    diagram.add_edge('users', 'user_types', LineType.STRAIGHT, Cardinality('0', '1'))  # users -> user_types (ゼロ対一)

    diagram.save_svg('er_diagram_example.svg')
    print("ER図をer_diagram_example.svgに出力しました。")

if __name__ == '__main__':
    main()
