# in4viz - インフラ構成図SVG描画ライブラリ

## プロジェクト概要

**in4viz** は、インフラ構成図をSVGで描画するためのTypeScriptライブラリです。自動レイアウト機能を中核とし、AWS/Azure/GCPなどのクラウドインフラを直感的に可視化できます。

## 基本方針

### 技術スタック
- **言語**: TypeScript
- **出力形式**: SVG
- **配布**: npm package + CDN (script tag対応)
- **フレームワーク対応**: React専用パッケージを別途提供 (`@infodb/in4viz-react`)

### ターゲット環境
- ブラウザ (ES2020+)
- Node.js (14+)
- React (別パッケージ)

## 機能要件

### Phase 1: AWS基本対応
- **リソース**: VPC, サブネット, EC2, RDS, S3, ELB等
- **自動レイアウト**: 階層構造（VPC > サブネット > EC2）の適切な配置
- **基本描画**: アイコン、ラベル、接続線

### Phase 2: 拡張機能
- **クラウド拡張**: Azure, GCP対応
- **高度なレイアウト**: Force-directed layout, 最適化アルゴリズム
- **インタラクション**: ズーム, パン, ホバー効果

### Phase 3: 高度な機能
- **カスタマイズ**: テーマ, スタイル設定
- **エクスポート**: PNG, PDF出力
- **アニメーション**: 状態変化の可視化

## アーキテクチャ設計

### パッケージ構成
```
@infodb/in4viz           # コアライブラリ
@infodb/in4viz-react     # React向けWrapper
@infodb/in4viz-icons     # アイコンパック (将来)
```

### モジュール構成 (予定)
```
src/
├── core/                # コア機能
│   ├── renderer/        # SVG描画エンジン
│   ├── layout/          # 自動レイアウトエンジン
│   └── geometry/        # 座標計算
├── providers/           # クラウドプロバイダー定義
│   ├── aws/
│   ├── azure/
│   └── gcp/
├── types/               # TypeScript型定義
└── utils/               # ユーティリティ
```

## データ構造 (草案)

### インフラ定義
```typescript
interface Infrastructure {
  id: string;
  provider: 'aws' | 'azure' | 'gcp';
  resources: Resource[];
  connections: Connection[];
}

interface Resource {
  id: string;
  type: string;        // 'vpc', 'subnet', 'ec2', etc.
  name: string;
  properties: Record<string, any>;
  parent?: string;     // 親リソースID
  position?: Point;    // 手動配置用
}

interface Connection {
  from: string;        // リソースID
  to: string;
  type: 'network' | 'dependency' | 'data';
  properties?: Record<string, any>;
}
```

### レイアウト結果
```typescript
interface LayoutResult {
  resources: PositionedResource[];
  connections: PositionedConnection[];
  bounds: Rectangle;
}

interface PositionedResource extends Resource {
  position: Point;
  size: Size;
  bounds: Rectangle;
}
```

## API設計 (草案)

### 基本API
```typescript
// インスタンス作成
const diagram = new In4viz(containerElement);

// データ設定
diagram.setData(infrastructureData);

// レンダリング
diagram.render();

// レイアウトオプション
diagram.setLayoutOptions({
  algorithm: 'hierarchical',
  spacing: { x: 100, y: 80 },
  autoFit: true
});
```

### React API (別パッケージ)
```typescript
<In4vizDiagram 
  data={infrastructureData}
  layout="hierarchical"
  onResourceClick={handleClick}
  width={800}
  height={600}
/>
```

---

## 開発TODO

### Phase 1: 基盤構築 (2-3週間)

#### 1.1 プロジェクト初期化
- [ ] **TypeScriptプロジェクト設定**
  - package.json, tsconfig.json, rollup/webpack設定
  - ESLint, Prettier設定
  - テスト環境 (Jest) 設定

- [ ] **基本的なディレクトリ構造作成**
  - src/, dist/, examples/, docs/ フォルダ
  - モジュール分割の骨組み

#### 1.2 コアデータ構造定義
- [ ] **TypeScript型定義を詳細化**
  - Infrastructure, Resource, Connection型の完全定義
  - AWS基本リソース型 (VPC, Subnet, EC2, RDS等) の定義
  - バリデーション機能

- [ ] **データ変換・正規化機能**
  - 入力データの検証
  - 階層構造の構築 (parent-child関係)

#### 1.3 SVG描画エンジン (基本版)
- [ ] **SVG基本描画クラス実装**
  - SVGElement生成・管理
  - 基本図形 (矩形, 円, 線, テキスト) 描画
  - レイヤー管理 (背景, リソース, 接続線, UI)

- [ ] **リソース描画機能**
  - 基本的なボックス描画
  - アイコン配置 (最初は基本図形で代用)
  - ラベル描画

#### 1.4 簡易レイアウトエンジン
- [ ] **階層レイアウト実装**
  - VPC > Subnet > EC2 等の親子関係配置
  - 基本的なスペーシング計算
  - 境界ボックス計算

- [ ] **接続線描画**
  - 直線接続の実装
  - 矢印、ラベル付きライン

### Phase 2: 基本機能完成 (3-4週間)

#### 2.1 AWS基本リソース対応拡張
- [ ] **主要AWSサービス型定義**
  - 20-30の基本サービス (EC2, RDS, S3, Lambda, ALB等)
  - サービス固有プロパティの定義

- [ ] **アイコンシステム**
  - SVGアイコンの管理システム
  - AWS公式アイコンの組み込み (ライセンス確認要)

#### 2.2 レイアウトアルゴリズム改善
- [ ] **高度な自動レイアウト**
  - Force-directed layoutの実装
  - 重複回避アルゴリズム
  - 最適化 (アニーリング等)

- [ ] **レイアウトオプション**
  - 複数アルゴリズムの選択機能
  - スペーシング、方向などの設定

#### 2.3 ユーザーインタラクション
- [ ] **基本的なUI機能**
  - ズーム、パン機能
  - リソースの選択、ホバー効果
  - ツールチップ表示

#### 2.4 配布準備
- [ ] **ビルドシステム整備**
  - UMD, ESM, CommonJS対応
  - TypeScript宣言ファイル生成
  - ミニファイ版の生成

- [ ] **パッケージング**
  - npm publish準備
  - CDN対応 (unpkg等)

### Phase 3: React対応・品質向上 (2-3週間)

#### 3.1 React専用パッケージ
- [ ] **@infodb/in4viz-react実装**
  - React Componentラッパー
  - Hooks (useIn4viz等)
  - React固有の最適化

#### 3.2 ドキュメント・例
- [ ] **ドキュメントサイト**
  - API リファレンス
  - チュートリアル
  - インタラクティブな例

- [ ] **サンプル集**
  - 典型的なAWS構成例
  - HTMLファイルでの使用例
  - React での使用例

#### 3.3 テスト・品質保証
- [ ] **自動テスト拡充**
  - ユニットテスト (90%+ カバレッジ)
  - E2Eテスト (Playwright等)
  - ビジュアルリグレッションテスト

- [ ] **性能最適化**
  - 大規模ダイアグラムでの性能測定
  - メモリリーク検証
  - バンドルサイズ最適化

---

## 技術的検討事項

### 自動レイアウトアルゴリズム
1. **階層レイアウト**: Sugiyama法ベース、グラフの階層構造可視化
2. **Force-directed**: D3.js参考、物理シミュレーション
3. **制約ベース**: VPC境界等の制約を満たすレイアウト

### SVG vs Canvas
- **SVG採用理由**: DOM操作可能、スケーラブル、アクセシビリティ
- **課題**: 大規模図面での性能、複雑な描画

### 依存関係最小化
- D3.js: 一部機能のみ (座標計算等) を参考実装
- 独自実装で軽量化を目指す

---

## リリース計画

### v0.1.0 (MVP) - 6週間後
- AWS基本リソース対応
- 階層レイアウト
- SVG描画
- npm配布

### v0.2.0 - 8週間後  
- React対応
- インタラクション機能
- ドキュメント整備

### v1.0.0 - 12週間後
- 安定版リリース
- 性能最適化完了
- フルテストカバレッジ
