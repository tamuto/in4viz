#!/usr/bin/env python3

from planning import ERDiagram
from planning.diagram import Table, Column, LineType

def main():
    diagram = ERDiagram()

    # ユーザーテーブル
    users_table = Table(
        name='users',
        logical_name='ユーザー',
        columns=[
            Column('id', 'ユーザーID', 'INT', primary_key=True, nullable=False),
            Column('username', 'ユーザー名', 'VARCHAR(50)', nullable=False),
            Column('email', 'メールアドレス', 'VARCHAR(100)', nullable=False),
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
            Column('user_id', 'ユーザーID', 'INT', nullable=False, foreign_key=True),
            Column('title', 'タイトル', 'VARCHAR(200)', nullable=False),
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

    # エッジ（関係線）の追加 - 物理テーブル名を使用
    diagram.add_edge('posts', 'users', LineType.STRAIGHT)  # posts -> users (直線)
    diagram.add_edge('post_categories', 'posts', LineType.STRAIGHT)  # post_categories -> posts
    diagram.add_edge('post_categories', 'categories', LineType.STRAIGHT)  # post_categories -> categories
    diagram.add_edge('user_types', 'users', LineType.STRAIGHT)  # user_types -> users

    diagram.save_svg('er_diagram_example.svg')
    print("ER図をer_diagram_example.svgに出力しました。")

if __name__ == '__main__':
    main()
