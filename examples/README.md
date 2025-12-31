# in4viz サンプル集

このディレクトリには、in4vizライブラリの使用例が含まれています。

## サンプルファイル

### basic_usage.py
統合APIを使用した基本的な使い方のサンプル。SVGとdraw.io両方の形式で出力します。

**実行方法:**
```bash
cd /kira/in4viz.feature-reset
PYTHONPATH=packages:$PYTHONPATH python3 examples/basic_usage.py
```

**出力:**
- `examples/er_diagram_example.svg` - SVG形式のER図
- `examples/er_diagram_example.drawio` - draw.io形式のER図

**内容:**
- ユーザー、投稿、カテゴリ、投稿カテゴリの4テーブル
- 複数のFK関係
- クランク線の使用例

---

### svg_example.py
SVGバックエンドを直接使用したサンプル。ブログシステムのER図を作成します。

**実行方法:**
```bash
cd /kira/in4viz.feature-reset
PYTHONPATH=packages:$PYTHONPATH python3 examples/svg_example.py
```

**出力:**
- `examples/blog_system.svg` - ブログシステムのER図

**内容:**
- ユーザー、プロフィール、投稿、コメントの4テーブル
- 1対1、1対多のリレーションシップ
- スプライン曲線の使用例

**特徴:**
- より詳細なカラム定義
- 異なる線種（SPLINE）の使用

---

### drawio_example.py
draw.ioバックエンドを直接使用したサンプル。注文管理システムのER図を作成します。

**実行方法:**
```bash
cd /kira/in4viz.feature-reset
PYTHONPATH=packages:$PYTHONPATH python3 examples/drawio_example.py
```

**出力:**
- `examples/order_system.drawio` - 注文管理システムのER図

**内容:**
- 顧客、注文、商品、注文明細の4テーブル
- 中間テーブル（注文明細）の使用例
- クランク線の使用例

**特徴:**
- ECサイトの典型的なデータ構造
- draw.io形式での編集が可能

---

## 実行前の準備

すべてのサンプルは、PYTHONPATHに`packages`ディレクトリを追加して実行します：

```bash
# プロジェクトルートに移動
cd /kira/in4viz.feature-reset

# 任意のサンプルを実行
PYTHONPATH=packages:$PYTHONPATH python3 examples/basic_usage.py
PYTHONPATH=packages:$PYTHONPATH python3 examples/svg_example.py
PYTHONPATH=packages:$PYTHONPATH python3 examples/drawio_example.py
```

または、一括で実行：

```bash
cd /kira/in4viz.feature-reset
for script in examples/*.py; do
    echo "Running $script..."
    PYTHONPATH=packages:$PYTHONPATH python3 "$script"
    echo
done
```

## 出力ファイルの確認方法

### SVGファイル
- ブラウザで直接開く（Chrome, Firefox, Safari など）
- VS CodeやテキストエディタでXMLとして表示

### draw.ioファイル
- https://app.diagrams.net/ で開く
- draw.ioデスクトップアプリで開く
- VS Codeのdraw.io拡張機能で開く

## カスタマイズのヒント

### 線種の変更
```python
from in4viz import LineType

# 直線
diagram.add_edge('table1', 'table2', line_type=LineType.STRAIGHT)

# クランク（直角）
diagram.add_edge('table1', 'table2', line_type=LineType.CRANK)

# スプライン（曲線）
diagram.add_edge('table1', 'table2', line_type=LineType.SPLINE)
```

### カーディナリティの指定
```python
from in4viz import Cardinality

# 1対多
Cardinality(from_side='*', to_side='1')

# 1対1
Cardinality(from_side='1', to_side='1')

# 0または1対多
Cardinality(from_side='*', to_side='0..1')

# 多対多
Cardinality(from_side='*', to_side='*')
```

### 手動配置
```python
# 座標を指定してテーブルを配置
diagram.add_table(users_table, x=100, y=100)
diagram.add_table(posts_table, x=500, y=100)

# 後から位置を変更
diagram.set_node_position('users', x=200, y=150)
```

## トラブルシューティング

### ModuleNotFoundError: No module named 'in4viz'
PYTHONPATHが正しく設定されているか確認してください：
```bash
PYTHONPATH=packages:$PYTHONPATH python3 examples/basic_usage.py
```

### 出力ファイルが見つからない
サンプルスクリプトは`examples/`ディレクトリ内にファイルを出力します。

## 参考資料

- [in4vizライブラリドキュメント](../packages/in4viz/README.md)
- [draw.io公式サイト](https://www.diagrams.net/)
