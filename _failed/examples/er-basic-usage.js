// ER図の基本的な使用例

const { In4viz } = require('../packages/core/dist/index.js');

// サンプルER図データ
const sampleERData = {
  tables: [
    {
      id: 'users',
      name: 'users',
      schema: 'public',
      columns: [
        { name: 'id', type: 'SERIAL', primaryKey: true, nullable: false },
        { name: 'email', type: 'VARCHAR(255)', unique: true, nullable: false },
        { name: 'name', type: 'VARCHAR(100)', nullable: false },
        { name: 'created_at', type: 'TIMESTAMP', defaultValue: 'NOW()' },
        { name: 'updated_at', type: 'TIMESTAMP', defaultValue: 'NOW()' }
      ]
    },
    {
      id: 'posts',
      name: 'posts',
      schema: 'public', 
      columns: [
        { name: 'id', type: 'SERIAL', primaryKey: true, nullable: false },
        { name: 'user_id', type: 'INTEGER', foreignKey: true, nullable: false },
        { name: 'title', type: 'VARCHAR(200)', nullable: false },
        { name: 'content', type: 'TEXT', nullable: true },
        { name: 'published', type: 'BOOLEAN', defaultValue: false },
        { name: 'created_at', type: 'TIMESTAMP', defaultValue: 'NOW()' }
      ]
    },
    {
      id: 'comments',
      name: 'comments',
      schema: 'public',
      columns: [
        { name: 'id', type: 'SERIAL', primaryKey: true, nullable: false },
        { name: 'post_id', type: 'INTEGER', foreignKey: true, nullable: false },
        { name: 'user_id', type: 'INTEGER', foreignKey: true, nullable: false },
        { name: 'content', type: 'TEXT', nullable: false },
        { name: 'created_at', type: 'TIMESTAMP', defaultValue: 'NOW()' }
      ]
    },
    {
      id: 'tags',
      name: 'tags', 
      schema: 'public',
      columns: [
        { name: 'id', type: 'SERIAL', primaryKey: true, nullable: false },
        { name: 'name', type: 'VARCHAR(50)', unique: true, nullable: false },
        { name: 'color', type: 'VARCHAR(7)', defaultValue: '#CCCCCC' }
      ]
    },
    {
      id: 'post_tags',
      name: 'post_tags',
      schema: 'public',
      columns: [
        { name: 'post_id', type: 'INTEGER', primaryKey: true, foreignKey: true, nullable: false },
        { name: 'tag_id', type: 'INTEGER', primaryKey: true, foreignKey: true, nullable: false },
        { name: 'created_at', type: 'TIMESTAMP', defaultValue: 'NOW()' }
      ]
    }
  ],
  relations: [
    {
      id: 'users_posts',
      from: { table: 'users', column: 'id' },
      to: { table: 'posts', column: 'user_id' },
      type: 'one-to-many',
      name: 'user_posts',
      onDelete: 'CASCADE'
    },
    {
      id: 'posts_comments',
      from: { table: 'posts', column: 'id' },
      to: { table: 'comments', column: 'post_id' },
      type: 'one-to-many',
      name: 'post_comments',
      onDelete: 'CASCADE'
    },
    {
      id: 'users_comments',
      from: { table: 'users', column: 'id' },
      to: { table: 'comments', column: 'user_id' },
      type: 'one-to-many',
      name: 'user_comments',
      onDelete: 'SET NULL'
    },
    {
      id: 'posts_post_tags',
      from: { table: 'posts', column: 'id' },
      to: { table: 'post_tags', column: 'post_id' },
      type: 'one-to-many',
      name: 'post_post_tags',
      onDelete: 'CASCADE'
    },
    {
      id: 'tags_post_tags',
      from: { table: 'tags', column: 'id' },
      to: { table: 'post_tags', column: 'tag_id' },
      type: 'one-to-many',
      name: 'tag_post_tags',
      onDelete: 'CASCADE'
    }
  ],
  metadata: {
    name: 'Blog Database',
    version: '1.0',
    description: 'Simple blog database schema'
  }
};

// ヘッドレスモードでER図を作成（Node.js環境での例）
function createERDiagramExample() {
  console.log('=== In4viz ER図 基本使用例 ===\n');
  
  // ER図の作成
  const erDiagram = new In4viz({ type: 'er', headless: true });
  
  console.log('1. ER図データを設定...');
  erDiagram.setERData(sampleERData);
  
  console.log('2. レイアウトを適用...');
  erDiagram.applyERLayout({ 
    algorithm: 'dagre', 
    direction: 'TB',
    fit: true
  });
  
  console.log('3. テーブル検索のテスト...');
  const userTables = erDiagram.findTables(table => table.name.includes('user'));
  console.log(`   - "user"を含むテーブル: ${userTables.map(t => t.name).join(', ')}`);
  
  console.log('4. 低次元API操作のテスト...');
  
  // 新しいテーブルを追加
  const newTable = {
    id: 'categories',
    name: 'categories',
    columns: [
      { name: 'id', type: 'SERIAL', primaryKey: true, nullable: false },
      { name: 'name', type: 'VARCHAR(100)', nullable: false },
      { name: 'description', type: 'TEXT' }
    ]
  };
  
  erDiagram.addTable(newTable);
  console.log('   - 新しいテーブル "categories" を追加');
  
  // リレーションを追加
  const newRelation = {
    id: 'posts_categories',
    from: { table: 'categories', column: 'id' },
    to: { table: 'posts', column: 'category_id' },
    type: 'one-to-many',
    name: 'category_posts'
  };
  
  // 最初にpostsテーブルにcategory_idカラムを追加
  erDiagram.updateTable('posts', {
    ...sampleERData.tables.find(t => t.id === 'posts'),
    columns: [
      ...sampleERData.tables.find(t => t.id === 'posts').columns,
      { name: 'category_id', type: 'INTEGER', foreignKey: true }
    ]
  });
  
  erDiagram.addRelation(newRelation);
  console.log('   - 新しいリレーション "posts_categories" を追加');
  
  console.log('5. 最終的なER図データを取得...');
  const finalERData = erDiagram.getERData();
  console.log(`   - テーブル数: ${finalERData.tables.length}`);
  console.log(`   - リレーション数: ${finalERData.relations.length}`);
  console.log(`   - テーブル一覧: ${finalERData.tables.map(t => t.name).join(', ')}`);
  
  console.log('\n6. ER図の操作完了');
  
  // クリーンアップ
  erDiagram.destroy();
  
  return finalERData;
}

// 実行
if (require.main === module) {
  try {
    createERDiagramExample();
    console.log('\n✅ ER図の基本機能テスト完了');
  } catch (error) {
    console.error('\n❌ エラーが発生しました:', error.message);
    console.error(error.stack);
  }
}

module.exports = { sampleERData, createERDiagramExample };