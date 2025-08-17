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

### パッケージ構成 ✅ **実装済み (2025/06/01)**
```
@infodb/in4viz-monorepo  # モノレポルート (private)
├── @infodb/in4viz       # コアライブラリ ✅ **ビルド成功**
└── @infodb/in4viz-react # React向けWrapper 📋 **TODO**
```

**実際のディレクトリ構成:**
```
in4viz/
├── packages/
│   ├── core/            # @infodb/in4viz ✅ **完全実装済み**
│   │   ├── dist/        # ✅ ビルド成果物 (ESM/CJS/DTS)
│   │   └── src/         # ✅ 完全実装済み
│   └── react/           # @infodb/in4viz-react 📋 **基本構造のみ**
├── examples/            # ✅ サンプル・デモ作成済み
├── docs/                # ドキュメント
├── tools/               # ビルドツール等
├── tsconfig.base.json   # 共通TypeScript設定
├── .eslintrc.js         # ESLint設定
└── .prettierrc.json     # Prettier設定
```

### モジュール構成
**現在の実装状況:**
```
packages/core/src/       # ✅ **完全実装済み** 
├── types/               # ✅ **完了**: 完全なTypeScript型定義システム
│   ├── common.ts        # ✅ 基本型 (Point, Size, Rectangle等)
│   ├── infrastructure.ts # ✅ インフラ構造型
│   ├── aws.ts           # ✅ AWS リソース型定義
│   ├── azure.ts         # ✅ Azure リソース型定義  
│   ├── gcp.ts           # ✅ GCP リソース型定義
│   ├── layout.ts        # ✅ レイアウト型定義
│   ├── renderer.ts      # ✅ レンダラー型定義
│   └── providers.ts     # ✅ プロバイダー型定義
├── core/                # ✅ **完了**: 完全なコア機能実装
│   ├── renderer/        # ✅ **完了**: SVG描画エンジン
│   │   ├── svg-renderer.ts # ✅ メインSVGレンダラー
│   │   ├── svg-utils.ts    # ✅ SVGユーティリティ
│   │   ├── icon-registry.ts # ✅ アイコン管理システム
│   │   └── themes.ts       # ✅ テーマシステム
│   ├── layout/          # ✅ **完了**: 自動レイアウトエンジン
│   │   ├── hierarchical.ts # ✅ 階層レイアウトアルゴリズム
│   │   └── manager.ts      # ✅ レイアウト管理
│   └── geometry/        # ✅ **完了**: 座標計算システム
│       └── utils.ts        # ✅ 幾何学計算ユーティリティ
├── providers/           # ✅ **完了**: クラウドプロバイダー定義
│   ├── aws/             # ✅ AWS プロバイダー (ヘルパー関数付き)
│   ├── azure/           # ✅ Azure プロバイダー
│   └── gcp/             # ✅ GCP プロバイダー
├── utils/               # ✅ **完了**: ユーティリティシステム
│   ├── data-validator.ts # ✅ データ検証
│   └── data.ts          # ✅ データ正規化
├── In4viz.ts           # ✅ **完了**: メインライブラリクラス
└── index.ts            # ✅ 完全なエクスポート定義

packages/react/src/      # 📋 **基本構造のみ** (次の実装対象)
├── components/          # 📋 TODO: React Components
├── hooks/               # 📋 TODO: React Hooks
└── index.tsx           # 📋 基本構造のみ
```

## データ構造 ✅ **実装済み**

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

## API設計 ✅ **実装済み**

### 基本API
```typescript
// 簡単なインスタンス作成（引数なしでOK）
const in4viz = new In4viz();

// Node.js環境でのヘッドレス実行
const svgString = in4viz.renderToString(infrastructureData, {
  algorithm: 'hierarchical',
  spacing: { x: 120, y: 100 },
  autoFit: true
});

// ブラウザ環境でのDOM要素作成
const svgElement = in4viz.render(infrastructureData, layoutOptions);

// AWS プロバイダーヘルパー
const awsProvider = new AWSProvider();
const vpc = awsProvider.createVPC('my-vpc', { cidr: '10.0.0.0/16' });
```

### React API (別パッケージ) 📋 **TODO**
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

## 🚀 プロジェクト進捗状況

### ✅ **完了済み (2025/06/01)**
1. **モノレポ構成設定** - pnpm workspaces, パッケージ構造
2. **ビルドシステム設定** - tsup による ESM/CJS 対応
3. **開発環境整備** - ESLint, Prettier, TypeScript 5.8
4. **tsconfig.json 改善** - モダンな設定への更新
5. **🎉 Phase 1 コアライブラリ完全実装** - 全機能実装完了
6. **✅ ビルド成功** - ESM/CJS/TypeScript宣言ファイル生成
7. **📦 配布可能パッケージ** - npm publish準備完了
8. **🚀 Node.js環境対応** - ヘッドレス実行、モックDOM、引数なしコンストラクタ
9. **⚡ API改善** - `renderToString()`メソッド、自動環境検出

### 🔄 **現在の状況**
- **✅ コアライブラリ**: 完全実装済み、Node.js対応完了、ビルド成功
- **⚡ 重要な改善**: 引数なしコンストラクタ対応、ヘッドレス実行可能
- **📋 React package**: 基本構造のみ（次の実装対象）

### 🆕 **最新の成果 (2025/06/01)**
```typescript
// 新しい使いやすいAPI
const in4viz = new In4viz(); // 引数なしでOK！
const svgString = in4viz.renderToString(data, layoutOptions);
// Node.js環境でも完全動作
```

### 📋 **今後のステップ**
1. **React wrapper実装** - @infodb/in4viz-react の完全実装
2. **サンプル・デモ拡充** - より多くの使用例作成
3. **ドキュメント作成** - API リファレンス、チュートリアル

---

## 🔄 開発TODO (継続的に更新)

> **このセクションは開発進捗に応じて継続的に更新されます**  
> 最終更新: **2025年6月1日**

### Phase 1: 基盤構築 ✅ **完了** (予定3週間 → 実際1日で完了)

#### 1.1 プロジェクト初期化 ✅ **完了**
- [x] **TypeScriptプロジェクト設定**
  - [x] package.json, tsconfig.json, tsup設定
  - [x] ESLint, Prettier設定
  - [ ] テスト環境 (Jest) 設定

- [x] **基本的なディレクトリ構造作成**
  - [x] packages/, examples/, docs/ フォルダ
  - [x] モノレポ構成とワークスペース設定

#### 1.2 コアデータ構造定義 ✅ **完了**
- [x] **TypeScript型定義を詳細化**
  - [x] Infrastructure, Resource, Connection型の完全定義
  - [x] AWS基本リソース型 (VPC, Subnet, EC2, RDS等) の定義
  - [x] Azure, GCP リソース型定義（基本構造）
  - [x] バリデーション機能

- [x] **データ変換・正規化機能**
  - [x] 入力データの検証 (DataValidator)
  - [x] データ正規化 (DataNormalizer)
  - [x] 階層構造の構築 (parent-child関係)

#### 1.3 SVG描画エンジン (基本版) ✅ **完了**
- [x] **SVG基本描画クラス実装**
  - [x] SVGElement生成・管理 (SVGUtils)
  - [x] 基本図形 (矩形, 円, 線, テキスト) 描画
  - [x] レイヤー管理 (背景, リソース, 接続線, UI)
  - [x] テーマシステム (defaultTheme, awsTheme等)

- [x] **リソース描画機能**
  - [x] 基本的なボックス描画 (DefaultSVGRenderer)
  - [x] アイコン管理システム (IconRegistry)
  - [x] ラベル描画機能

#### 1.4 簡易レイアウトエンジン ✅ **完了**
- [x] **階層レイアウト実装**
  - [x] VPC > Subnet > EC2 等の親子関係配置
  - [x] 基本的なスペーシング計算 (GeometryUtils)
  - [x] 境界ボックス計算
  - [x] レイアウト管理システム (LayoutManager)

- [x] **接続線描画**
  - [x] 直線接続の実装
  - [x] 矢印、ラベル付きライン
  - [x] 接続線のレイアウト計算

#### 1.5 統合・ビルドシステム ✅ **完了**
- [x] **メインライブラリクラス (In4viz)**
  - [x] 統合API実装
  - [x] レンダリングパイプライン
  - [x] オプション管理
- [x] **ビルド成功**
  - [x] ESM形式 (51.43 KB)
  - [x] CommonJS形式 (51.85 KB)  
  - [x] TypeScript宣言ファイル (27.86 KB)
- [x] **サンプル実装**
  - [x] 基本使用例作成
  - [x] AWS プロバイダーヘルパー

### Phase 2: 基本機能完成 📋 **次の実装対象** (3-4週間)

#### 2.1 React wrapper実装 📋 **優先TODO**
- [ ] **@infodb/in4viz-react パッケージ**
  - [ ] In4vizDiagram React Component
  - [ ] useIn4viz Hook
  - [ ] React向け最適化
  - [ ] TypeScript 型定義

#### 2.2 AWS基本リソース対応拡張 📋 **TODO**
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
