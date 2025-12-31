"""SVG形式での出力例

このサンプルを実行するには:
    cd /kira/in4viz.feature-reset
    PYTHONPATH=packages:$PYTHONPATH python3 examples/svg_example.py
"""

import sys
from pathlib import Path

# パッケージへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages'))

from in4viz.backends.svg import SVGERDiagram
from in4viz import Table, Column, LineType, Cardinality


def main():
    """SVG形式でER図を作成"""
    print("Creating ER diagram in SVG format...")

    # SVGバックエンドを直接使用
    diagram = SVGERDiagram(default_line_type=LineType.SPLINE)

    # ユーザーテーブル
    users = Table(
        name='users',
        logical_name='ユーザー',
        columns=[
            Column('id', 'ユーザーID', 'BIGINT', primary_key=True, nullable=False),
            Column('username', 'ユーザー名', 'VARCHAR(50)', nullable=False, index=True),
            Column('email', 'メールアドレス', 'VARCHAR(255)', nullable=False, index=True),
            Column('password_hash', 'パスワードハッシュ', 'VARCHAR(255)', nullable=False),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False),
            Column('updated_at', '更新日時', 'TIMESTAMP', nullable=False),
        ]
    )

    # プロフィールテーブル
    profiles = Table(
        name='user_profiles',
        logical_name='ユーザープロフィール',
        columns=[
            Column('user_id', 'ユーザーID', 'BIGINT', primary_key=True, nullable=False, foreign_key=True),
            Column('display_name', '表示名', 'VARCHAR(100)'),
            Column('bio', '自己紹介', 'TEXT'),
            Column('avatar_url', 'アバター画像URL', 'VARCHAR(500)'),
            Column('website', 'ウェブサイト', 'VARCHAR(255)'),
        ]
    )

    # 投稿テーブル
    posts = Table(
        name='posts',
        logical_name='投稿',
        columns=[
            Column('id', '投稿ID', 'BIGINT', primary_key=True, nullable=False),
            Column('user_id', 'ユーザーID', 'BIGINT', nullable=False, foreign_key=True, index=True),
            Column('title', 'タイトル', 'VARCHAR(200)', nullable=False),
            Column('content', '本文', 'TEXT', nullable=False),
            Column('status', 'ステータス', 'VARCHAR(20)', nullable=False),
            Column('published_at', '公開日時', 'TIMESTAMP'),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False),
        ]
    )

    # コメントテーブル
    comments = Table(
        name='comments',
        logical_name='コメント',
        columns=[
            Column('id', 'コメントID', 'BIGINT', primary_key=True, nullable=False),
            Column('post_id', '投稿ID', 'BIGINT', nullable=False, foreign_key=True, index=True),
            Column('user_id', 'ユーザーID', 'BIGINT', nullable=False, foreign_key=True, index=True),
            Column('content', 'コメント内容', 'TEXT', nullable=False),
            Column('created_at', '作成日時', 'TIMESTAMP', nullable=False),
        ]
    )

    # テーブルを追加
    diagram.add_table(users)
    diagram.add_table(profiles)
    diagram.add_table(posts)
    diagram.add_table(comments)

    # リレーションシップを追加（スプライン曲線で）
    diagram.add_edge(
        'user_profiles', 'users',
        line_type=LineType.SPLINE,
        cardinality=Cardinality(from_side='1', to_side='1')
    )
    diagram.add_edge(
        'posts', 'users',
        line_type=LineType.SPLINE,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'comments', 'posts',
        line_type=LineType.SPLINE,
        cardinality=Cardinality(from_side='*', to_side='1')
    )
    diagram.add_edge(
        'comments', 'users',
        line_type=LineType.SPLINE,
        cardinality=Cardinality(from_side='*', to_side='1')
    )

    # SVGファイルとして保存
    output_path = Path(__file__).parent / 'blog_system.svg'
    diagram.save_svg(str(output_path))

    print(f"✓ SVG diagram saved to: {output_path}")
    print(f"  Open it in a web browser to view the ER diagram")


if __name__ == '__main__':
    main()
