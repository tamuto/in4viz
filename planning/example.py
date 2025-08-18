#!/usr/bin/env python3

from planning import ERDiagram

def main():
    diagram = ERDiagram(canvas_width=1200, canvas_height=600)

    users_columns = [
        {'name': 'id', 'logical_name': 'ユーザーID', 'type': 'INT', 'primary_key': True, 'nullable': False},
        {'name': 'username', 'logical_name': 'ユーザー名', 'type': 'VARCHAR(50)', 'primary_key': False, 'nullable': False},
        {'name': 'email', 'logical_name': 'メールアドレス', 'type': 'VARCHAR(100)', 'primary_key': False, 'nullable': False},
        {'name': 'created_at', 'logical_name': '作成日時', 'type': 'TIMESTAMP', 'primary_key': False, 'nullable': False}
    ]
    diagram.add_table('users', users_columns, logical_name='ユーザー')

    posts_columns = [
        {'name': 'id', 'logical_name': '投稿ID', 'type': 'INT', 'primary_key': True, 'nullable': False},
        {'name': 'user_id', 'logical_name': 'ユーザーID', 'type': 'INT', 'primary_key': False, 'nullable': False, 'foreign_key': True},
        {'name': 'title', 'logical_name': 'タイトル', 'type': 'VARCHAR(200)', 'primary_key': False, 'nullable': False},
        {'name': 'content', 'logical_name': '本文', 'type': 'TEXT', 'primary_key': False, 'nullable': True},
        {'name': 'published_at', 'logical_name': '公開日時', 'type': 'TIMESTAMP', 'primary_key': False, 'nullable': True}
    ]
    diagram.add_table('posts', posts_columns, logical_name='投稿')

    categories_columns = [
        {'name': 'id', 'logical_name': 'カテゴリID', 'type': 'INT', 'primary_key': True, 'nullable': False},
        {'name': 'name', 'logical_name': 'カテゴリ名', 'type': 'VARCHAR(100)', 'primary_key': False, 'nullable': False},
        {'name': 'description', 'logical_name': '説明', 'type': 'TEXT', 'primary_key': False, 'nullable': True}
    ]
    diagram.add_table('categories', categories_columns, logical_name='カテゴリ')

    post_categories_columns = [
        {'name': 'post_id', 'logical_name': '投稿ID', 'type': 'INT', 'primary_key': True, 'nullable': False, 'foreign_key': True},
        {'name': 'category_id', 'logical_name': 'カテゴリID', 'type': 'INT', 'primary_key': True, 'nullable': False, 'foreign_key': True}
    ]
    diagram.add_table('post_categories', post_categories_columns, logical_name='投稿カテゴリ')
    
    # ユーザ種別テーブルを追加
    user_types_columns = [
        {'name': 'id', 'logical_name': '種別ID', 'type': 'INT', 'primary_key': True, 'nullable': False},
        {'name': 'type_name', 'logical_name': '種別名', 'type': 'VARCHAR(50)', 'primary_key': False, 'nullable': False},
        {'name': 'description', 'logical_name': '説明', 'type': 'TEXT', 'primary_key': False, 'nullable': True}
    ]
    diagram.add_table('user_types', user_types_columns, logical_name='ユーザ種別')

    # エッジ（関係線）の追加 - 異なる線種でテスト
    from planning.diagram import LineType
    diagram.add_edge('table_1', 'table_0', LineType.STRAIGHT)  # posts -> users (直線)
    diagram.add_edge('table_3', 'table_1', LineType.STRAIGHT)  # post_categories -> posts
    diagram.add_edge('table_3', 'table_2', LineType.STRAIGHT)  # post_categories -> categories
    diagram.add_edge('table_4', 'table_0', LineType.STRAIGHT)  # user_types -> users

    diagram.save_svg('er_diagram_example.svg')
    print("ER図をer_diagram_example.svgに出力しました。")

if __name__ == '__main__':
    main()
