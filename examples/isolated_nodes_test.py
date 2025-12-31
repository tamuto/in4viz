"""孤立ノードのレイアウトテスト

接続されていないテーブル（孤立ノード）が
適切に配置されることを確認するテスト
"""

import sys
from pathlib import Path

# パッケージへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages'))

from in4viz import ERDiagram, Table, Column, LineType, Cardinality


def create_diagram_with_isolated_nodes():
    """孤立ノードを含むER図を作成"""
    print("Creating diagram with isolated nodes...")

    diagram = ERDiagram(backend='svg', default_line_type=LineType.CRANK)

    # === 接続されたテーブル群 ===
    users = Table(
        name='users',
        logical_name='ユーザー',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True),
            Column('name', '名前', 'VARCHAR(100)'),
            Column('email', 'メール', 'VARCHAR(255)'),
        ]
    )

    posts = Table(
        name='posts',
        logical_name='投稿',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True),
            Column('user_id', 'ユーザーID', 'INT', foreign_key=True),
            Column('title', 'タイトル', 'VARCHAR(200)'),
        ]
    )

    comments = Table(
        name='comments',
        logical_name='コメント',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True),
            Column('post_id', '投稿ID', 'INT', foreign_key=True),
            Column('user_id', 'ユーザーID', 'INT', foreign_key=True),
            Column('content', '内容', 'TEXT'),
        ]
    )

    # === 孤立テーブル（接続なし） ===
    settings = Table(
        name='settings',
        logical_name='設定',
        columns=[
            Column('key', 'キー', 'VARCHAR(100)', primary_key=True),
            Column('value', '値', 'TEXT'),
        ]
    )

    logs = Table(
        name='logs',
        logical_name='ログ',
        columns=[
            Column('id', 'ID', 'INT', primary_key=True),
            Column('message', 'メッセージ', 'TEXT'),
            Column('created_at', '作成日時', 'TIMESTAMP'),
        ]
    )

    master_data = Table(
        name='master_data',
        logical_name='マスターデータ',
        columns=[
            Column('code', 'コード', 'VARCHAR(50)', primary_key=True),
            Column('name', '名称', 'VARCHAR(100)'),
        ]
    )

    # テーブルを追加
    diagram.add_table(users)
    diagram.add_table(posts)
    diagram.add_table(comments)
    diagram.add_table(settings)      # 孤立
    diagram.add_table(logs)          # 孤立
    diagram.add_table(master_data)   # 孤立

    # 接続されたテーブル間のリレーション
    diagram.add_edge('posts', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('comments', 'posts', cardinality=Cardinality('*', '1'))
    diagram.add_edge('comments', 'users', cardinality=Cardinality('*', '1'))

    # SVGファイルとして保存
    output_path = Path(__file__).parent / 'isolated_nodes_test.svg'
    diagram.save(str(output_path))
    print(f"Saved to: {output_path}")

    return output_path


def main():
    print("Isolated Nodes Layout Test")
    print("=" * 50)
    print()
    print("接続されたテーブル: users, posts, comments")
    print("孤立テーブル: settings, logs, master_data")
    print()

    output = create_diagram_with_isolated_nodes()

    print()
    print("=" * 50)
    print("確認ポイント:")
    print("- 孤立テーブル(settings, logs, master_data)が")
    print("  接続グループの右側にコンパクトに配置されていること")
    print("- 遠くに飛ばされていないこと")


if __name__ == '__main__':
    main()
