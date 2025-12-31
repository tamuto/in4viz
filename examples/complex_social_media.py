"""複雑なソーシャルメディアプラットフォームのER図サンプル

12テーブルのSNSデータベース構造
ユーザー間の複雑な関係性を表現

このサンプルを実行するには:
    cd /kira/in4viz.feature-reset
    PYTHONPATH=packages:$PYTHONPATH python3 examples/complex_social_media.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'packages'))

from in4viz import ERDiagram, Table, Column, LineType, Cardinality


def create_social_media_tables():
    """ソーシャルメディアの全テーブルを作成"""

    # ユーザー関連
    users = Table('users', 'ユーザー', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('username', 'ユーザー名', 'VARCHAR(30)'),
        Column('email', 'メール', 'VARCHAR(255)'),
        Column('password_hash', 'パスワード', 'VARCHAR(255)'),
        Column('display_name', '表示名', 'VARCHAR(50)'),
        Column('bio', '自己紹介', 'VARCHAR(300)'),
        Column('avatar_url', 'アバター', 'VARCHAR(500)'),
        Column('is_verified', '認証済み', 'BOOLEAN'),
        Column('created_at', '登録日', 'TIMESTAMP'),
    ])

    # フォロー関係
    follows = Table('follows', 'フォロー', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('follower_id', 'フォロワーID', 'BIGINT', foreign_key=True),
        Column('following_id', 'フォロー先ID', 'BIGINT', foreign_key=True),
        Column('created_at', 'フォロー日', 'TIMESTAMP'),
    ])

    # 投稿
    posts = Table('posts', '投稿', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('content', '本文', 'TEXT'),
        Column('visibility', '公開範囲', 'VARCHAR(20)'),
        Column('reply_to_id', '返信先ID', 'BIGINT', foreign_key=True),
        Column('repost_of_id', 'リポスト元ID', 'BIGINT', foreign_key=True),
        Column('created_at', '投稿日時', 'TIMESTAMP'),
    ])

    # 投稿メディア
    post_media = Table('post_media', '投稿メディア', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('post_id', '投稿ID', 'BIGINT', foreign_key=True),
        Column('media_type', 'メディア種別', 'VARCHAR(20)'),
        Column('url', 'URL', 'VARCHAR(500)'),
        Column('alt_text', '代替テキスト', 'VARCHAR(200)'),
    ])

    # いいね
    likes = Table('likes', 'いいね', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('post_id', '投稿ID', 'BIGINT', foreign_key=True),
        Column('created_at', '日時', 'TIMESTAMP'),
    ])

    # ブックマーク
    bookmarks = Table('bookmarks', 'ブックマーク', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('post_id', '投稿ID', 'BIGINT', foreign_key=True),
        Column('created_at', '日時', 'TIMESTAMP'),
    ])

    # ハッシュタグ
    hashtags = Table('hashtags', 'ハッシュタグ', [
        Column('id', 'ID', 'INT', primary_key=True),
        Column('name', 'タグ名', 'VARCHAR(50)'),
        Column('post_count', '投稿数', 'INT'),
    ])

    # 投稿-ハッシュタグ関連
    post_hashtags = Table('post_hashtags', '投稿タグ', [
        Column('post_id', '投稿ID', 'BIGINT', primary_key=True, foreign_key=True),
        Column('hashtag_id', 'タグID', 'INT', primary_key=True, foreign_key=True),
    ])

    # ダイレクトメッセージ
    conversations = Table('conversations', '会話', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('created_at', '作成日', 'TIMESTAMP'),
        Column('updated_at', '更新日', 'TIMESTAMP'),
    ])

    conversation_members = Table('conversation_members', '会話メンバー', [
        Column('conversation_id', '会話ID', 'BIGINT', primary_key=True, foreign_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', primary_key=True, foreign_key=True),
        Column('joined_at', '参加日', 'TIMESTAMP'),
    ])

    messages = Table('messages', 'メッセージ', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('conversation_id', '会話ID', 'BIGINT', foreign_key=True),
        Column('sender_id', '送信者ID', 'BIGINT', foreign_key=True),
        Column('content', '内容', 'TEXT'),
        Column('sent_at', '送信日時', 'TIMESTAMP'),
    ])

    # 通知
    notifications = Table('notifications', '通知', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', '対象ユーザーID', 'BIGINT', foreign_key=True),
        Column('actor_id', '実行者ID', 'BIGINT', foreign_key=True),
        Column('type', '通知種別', 'VARCHAR(30)'),
        Column('post_id', '関連投稿ID', 'BIGINT', foreign_key=True),
        Column('is_read', '既読', 'BOOLEAN'),
        Column('created_at', '日時', 'TIMESTAMP'),
    ])

    return (users, follows, posts, post_media, likes, bookmarks,
            hashtags, post_hashtags, conversations, conversation_members,
            messages, notifications)


def main():
    """ソーシャルメディアのER図を作成"""
    print("Creating complex Social Media ER diagram...")
    print("(12 tables with self-references and many-to-many relationships)")
    print()

    diagram = ERDiagram(backend='svg', default_line_type=LineType.CRANK)

    tables = create_social_media_tables()
    (users, follows, posts, post_media, likes, bookmarks,
     hashtags, post_hashtags, conversations, conversation_members,
     messages, notifications) = tables

    for table in tables:
        diagram.add_table(table)

    # ユーザー関連
    diagram.add_edge('follows', 'users', cardinality=Cardinality('*', '1'))  # follower
    # follows -> users (following) は同じテーブルへの2つ目の参照

    # 投稿関連
    diagram.add_edge('posts', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('posts', 'posts', cardinality=Cardinality('*', '0..1'))  # 返信・リポスト
    diagram.add_edge('post_media', 'posts', cardinality=Cardinality('*', '1'))

    # いいね・ブックマーク
    diagram.add_edge('likes', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('likes', 'posts', cardinality=Cardinality('*', '1'))
    diagram.add_edge('bookmarks', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('bookmarks', 'posts', cardinality=Cardinality('*', '1'))

    # ハッシュタグ
    diagram.add_edge('post_hashtags', 'posts', cardinality=Cardinality('*', '1'))
    diagram.add_edge('post_hashtags', 'hashtags', cardinality=Cardinality('*', '1'))

    # ダイレクトメッセージ
    diagram.add_edge('conversation_members', 'conversations', cardinality=Cardinality('*', '1'))
    diagram.add_edge('conversation_members', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('messages', 'conversations', cardinality=Cardinality('*', '1'))
    diagram.add_edge('messages', 'users', cardinality=Cardinality('*', '1'))

    # 通知
    diagram.add_edge('notifications', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('notifications', 'posts', cardinality=Cardinality('*', '0..1'))

    # 保存
    output_path = Path(__file__).parent / 'complex_social_media.svg'
    diagram.save(str(output_path))
    print(f"SVG saved: {output_path}")

    # draw.io形式でも出力
    diagram_drawio = ERDiagram(backend='drawio', default_line_type=LineType.STRAIGHT)

    for table in tables:
        diagram_drawio.add_table(table)

    diagram_drawio.add_edge('follows', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('posts', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('posts', 'posts', cardinality=Cardinality('*', '0..1'))
    diagram_drawio.add_edge('post_media', 'posts', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('likes', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('likes', 'posts', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('bookmarks', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('bookmarks', 'posts', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('post_hashtags', 'posts', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('post_hashtags', 'hashtags', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('conversation_members', 'conversations', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('conversation_members', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('messages', 'conversations', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('messages', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('notifications', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('notifications', 'posts', cardinality=Cardinality('*', '0..1'))

    output_drawio = Path(__file__).parent / 'complex_social_media.drawio'
    diagram_drawio.save(str(output_drawio))
    print(f"draw.io saved: {output_drawio}")

    print()
    print("Done! Complex Social Media diagrams created.")
    print(f"  Tables: 12")
    print(f"  Relationships: 16")


if __name__ == '__main__':
    main()
