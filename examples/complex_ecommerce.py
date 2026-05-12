"""複雑なECサイトのER図サンプル

15テーブルの本格的なECサイトデータベース構造
多数のリレーションシップを持つ複雑なパターンを表示

このサンプルを実行するには:
    cd /kira/in4viz.feature-reset
    python3 examples/complex_ecommerce.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'packages' / 'in4viz' / 'src'))

from in4viz import Table, Column, LineType, Cardinality
from in4viz.backends.svg import SVGERDiagram
from in4viz.backends.drawio import DrawioERDiagram


def create_ecommerce_tables():
    """ECサイトの全テーブルを作成"""

    # ユーザー関連
    users = Table('users', 'ユーザー', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('email', 'メール', 'VARCHAR(255)', index=True),
        Column('password_hash', 'パスワード', 'VARCHAR(255)'),
        Column('name', '氏名', 'VARCHAR(100)'),
        Column('phone', '電話番号', 'VARCHAR(20)'),
        Column('created_at', '登録日', 'TIMESTAMP'),
    ])

    addresses = Table('addresses', '住所', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('postal_code', '郵便番号', 'VARCHAR(10)'),
        Column('prefecture', '都道府県', 'VARCHAR(10)'),
        Column('city', '市区町村', 'VARCHAR(50)'),
        Column('address', '住所', 'VARCHAR(200)'),
        Column('is_default', 'デフォルト', 'BOOLEAN'),
    ])

    # 商品関連
    categories = Table('categories', 'カテゴリ', [
        Column('id', 'ID', 'INT', primary_key=True),
        Column('parent_id', '親カテゴリID', 'INT', foreign_key=True),
        Column('name', 'カテゴリ名', 'VARCHAR(100)'),
        Column('slug', 'スラッグ', 'VARCHAR(100)'),
        Column('sort_order', '表示順', 'INT'),
    ])

    brands = Table('brands', 'ブランド', [
        Column('id', 'ID', 'INT', primary_key=True),
        Column('name', 'ブランド名', 'VARCHAR(100)'),
        Column('logo_url', 'ロゴURL', 'VARCHAR(500)'),
        Column('description', '説明', 'TEXT'),
    ])

    products = Table('products', '商品', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('category_id', 'カテゴリID', 'INT', foreign_key=True),
        Column('brand_id', 'ブランドID', 'INT', foreign_key=True),
        Column('name', '商品名', 'VARCHAR(200)'),
        Column('description', '説明', 'TEXT'),
        Column('price', '価格', 'DECIMAL(10,2)'),
        Column('stock', '在庫数', 'INT'),
        Column('is_active', '販売中', 'BOOLEAN'),
    ])

    product_images = Table('product_images', '商品画像', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('product_id', '商品ID', 'BIGINT', foreign_key=True),
        Column('image_url', '画像URL', 'VARCHAR(500)'),
        Column('sort_order', '表示順', 'INT'),
    ])

    product_variants = Table('product_variants', '商品バリエーション', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('product_id', '商品ID', 'BIGINT', foreign_key=True),
        Column('sku', 'SKU', 'VARCHAR(50)'),
        Column('size', 'サイズ', 'VARCHAR(20)'),
        Column('color', '色', 'VARCHAR(30)'),
        Column('price_diff', '価格差', 'DECIMAL(10,2)'),
        Column('stock', '在庫', 'INT'),
    ])

    # 注文関連
    orders = Table('orders', '注文', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('address_id', '配送先ID', 'BIGINT', foreign_key=True),
        Column('status', 'ステータス', 'VARCHAR(20)'),
        Column('total_amount', '合計金額', 'DECIMAL(12,2)'),
        Column('ordered_at', '注文日時', 'TIMESTAMP'),
    ])

    order_items = Table('order_items', '注文明細', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('order_id', '注文ID', 'BIGINT', foreign_key=True),
        Column('product_id', '商品ID', 'BIGINT', foreign_key=True),
        Column('variant_id', 'バリエーションID', 'BIGINT', foreign_key=True),
        Column('quantity', '数量', 'INT'),
        Column('unit_price', '単価', 'DECIMAL(10,2)'),
    ])

    # 決済関連
    payments = Table('payments', '決済', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('order_id', '注文ID', 'BIGINT', foreign_key=True),
        Column('method', '決済方法', 'VARCHAR(30)'),
        Column('amount', '金額', 'DECIMAL(12,2)'),
        Column('status', 'ステータス', 'VARCHAR(20)'),
        Column('paid_at', '決済日時', 'TIMESTAMP'),
    ])

    # 配送関連
    shipments = Table('shipments', '配送', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('order_id', '注文ID', 'BIGINT', foreign_key=True),
        Column('carrier', '配送業者', 'VARCHAR(50)'),
        Column('tracking_no', '追跡番号', 'VARCHAR(50)'),
        Column('status', 'ステータス', 'VARCHAR(20)'),
        Column('shipped_at', '発送日', 'TIMESTAMP'),
    ])

    # レビュー・お気に入り
    reviews = Table('reviews', 'レビュー', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('product_id', '商品ID', 'BIGINT', foreign_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('rating', '評価', 'INT'),
        Column('title', 'タイトル', 'VARCHAR(100)'),
        Column('comment', 'コメント', 'TEXT'),
        Column('created_at', '投稿日', 'TIMESTAMP'),
    ])

    wishlists = Table('wishlists', 'お気に入り', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('product_id', '商品ID', 'BIGINT', foreign_key=True),
        Column('added_at', '追加日', 'TIMESTAMP'),
    ])

    # カート
    cart_items = Table('cart_items', 'カート', [
        Column('id', 'ID', 'BIGINT', primary_key=True),
        Column('user_id', 'ユーザーID', 'BIGINT', foreign_key=True),
        Column('product_id', '商品ID', 'BIGINT', foreign_key=True),
        Column('variant_id', 'バリエーションID', 'BIGINT', foreign_key=True),
        Column('quantity', '数量', 'INT'),
    ])

    # クーポン
    coupons = Table('coupons', 'クーポン', [
        Column('id', 'ID', 'INT', primary_key=True),
        Column('code', 'クーポンコード', 'VARCHAR(30)'),
        Column('discount_type', '割引タイプ', 'VARCHAR(20)'),
        Column('discount_value', '割引値', 'DECIMAL(10,2)'),
        Column('valid_from', '有効開始', 'TIMESTAMP'),
        Column('valid_until', '有効期限', 'TIMESTAMP'),
    ])

    return (users, addresses, categories, brands, products, product_images,
            product_variants, orders, order_items, payments, shipments,
            reviews, wishlists, cart_items, coupons)


def main():
    """ECサイトのER図を作成"""
    print("Creating complex E-commerce ER diagram...")
    print("(15 tables with multiple relationships)")
    print()

    # SVG形式で出力
    diagram = SVGERDiagram(default_line_type=LineType.CRANK)

    tables = create_ecommerce_tables()
    (users, addresses, categories, brands, products, product_images,
     product_variants, orders, order_items, payments, shipments,
     reviews, wishlists, cart_items, coupons) = tables

    # テーブルを追加
    for table in tables:
        diagram.add_table(table)

    # リレーションシップを追加
    # ユーザー関連
    diagram.add_edge('addresses', 'users', cardinality=Cardinality('*', '1'))

    # 商品関連
    diagram.add_edge('categories', 'categories', cardinality=Cardinality('*', '0..1'))  # 自己参照
    diagram.add_edge('products', 'categories', cardinality=Cardinality('*', '1'))
    diagram.add_edge('products', 'brands', cardinality=Cardinality('*', '1'))
    diagram.add_edge('product_images', 'products', cardinality=Cardinality('*', '1'))
    diagram.add_edge('product_variants', 'products', cardinality=Cardinality('*', '1'))

    # 注文関連
    diagram.add_edge('orders', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('orders', 'addresses', cardinality=Cardinality('*', '1'))
    diagram.add_edge('order_items', 'orders', cardinality=Cardinality('*', '1'))
    diagram.add_edge('order_items', 'products', cardinality=Cardinality('*', '1'))
    diagram.add_edge('order_items', 'product_variants', cardinality=Cardinality('*', '0..1'))

    # 決済・配送
    diagram.add_edge('payments', 'orders', cardinality=Cardinality('1', '1'))
    diagram.add_edge('shipments', 'orders', cardinality=Cardinality('*', '1'))

    # レビュー・お気に入り・カート
    diagram.add_edge('reviews', 'products', cardinality=Cardinality('*', '1'))
    diagram.add_edge('reviews', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('wishlists', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('wishlists', 'products', cardinality=Cardinality('*', '1'))
    diagram.add_edge('cart_items', 'users', cardinality=Cardinality('*', '1'))
    diagram.add_edge('cart_items', 'products', cardinality=Cardinality('*', '1'))
    diagram.add_edge('cart_items', 'product_variants', cardinality=Cardinality('*', '0..1'))

    # 保存
    output_path = Path(__file__).parent / 'complex_ecommerce.svg'
    diagram.save_svg(str(output_path))
    print(f"SVG saved: {output_path}")

    # draw.io形式でも出力
    diagram_drawio = DrawioERDiagram(default_line_type=LineType.STRAIGHT)

    for table in tables:
        diagram_drawio.add_table(table)

    # 同じリレーションシップを追加
    diagram_drawio.add_edge('addresses', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('categories', 'categories', cardinality=Cardinality('*', '0..1'))
    diagram_drawio.add_edge('products', 'categories', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('products', 'brands', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('product_images', 'products', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('product_variants', 'products', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('orders', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('orders', 'addresses', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('order_items', 'orders', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('order_items', 'products', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('order_items', 'product_variants', cardinality=Cardinality('*', '0..1'))
    diagram_drawio.add_edge('payments', 'orders', cardinality=Cardinality('1', '1'))
    diagram_drawio.add_edge('shipments', 'orders', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('reviews', 'products', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('reviews', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('wishlists', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('wishlists', 'products', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('cart_items', 'users', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('cart_items', 'products', cardinality=Cardinality('*', '1'))
    diagram_drawio.add_edge('cart_items', 'product_variants', cardinality=Cardinality('*', '0..1'))

    output_drawio = Path(__file__).parent / 'complex_ecommerce.drawio'
    diagram_drawio.save_drawio(str(output_drawio))
    print(f"draw.io saved: {output_drawio}")

    print()
    print("Done! Complex E-commerce diagrams created.")
    print(f"  Tables: 15")
    print(f"  Relationships: 20")


if __name__ == '__main__':
    main()
