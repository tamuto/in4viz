from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Stencil(ABC):
    def __init__(self, width: int = 200, height: int = 100):
        self.width = width
        self.height = height
    
    @abstractmethod
    def render(self, data: Dict[str, Any], x: int, y: int) -> str:
        pass


class TableStencil(Stencil):
    def __init__(self, width: int = 400, min_height: int = 100):
        super().__init__(width, min_height)
        self.min_height = min_height
        self.row_height = 22
        self.header_height = 25
        self.min_logical_width = 40  # 4文字分
        self.min_physical_width = 30  # 3文字分  
        self.min_data_type_width = 45  # 5文字分
        self.min_constraint_width = 60  # 8文字分（制約文字列対応）
        self.padding = 10
    
    def _calculate_text_width(self, text: str, is_japanese: bool = True) -> int:
        """テキストの幅を計算（日本語/英語を区別）"""
        if is_japanese:
            # 日本語文字は幅広（論理名用）
            return len(text) * 11
        else:
            # 英語文字は幅狭（物理名、型、制約用）
            return len(text) * 6
    
    def _calculate_widths(self, data: Dict[str, Any]) -> Dict[str, int]:
        physical_name = data.get('table_name', 'Table')
        logical_name = data.get('logical_name', physical_name)
        columns = data.get('columns', [])
        
        # テーブル名の幅計算（独立）
        logical_table_width = max(self.min_logical_width, self._calculate_text_width(logical_name, True) + self.padding)
        physical_table_width = max(self.min_physical_width, self._calculate_text_width(physical_name, False) + self.padding)
        table_total_width = logical_table_width + physical_table_width
        
        # カラム名の幅計算
        max_logical_col_width = self.min_logical_width
        max_physical_col_width = self.min_physical_width
        max_type_width = self.min_data_type_width
        max_constraint_width = self.min_constraint_width
        
        for column in columns:
            physical_col_name = column.get('name', '')
            logical_col_name = column.get('logical_name', physical_col_name)
            column_type = column.get('type', 'VARCHAR')
            
            # 制約文字列の計算（PKは除外）
            constraints = []
            if not column.get('nullable', True):
                constraints.append('NOT NULL')
            if column.get('foreign_key', False):
                constraints.append('FK')
            constraint_text = ', '.join(constraints) if constraints else ''
            
            max_logical_col_width = max(max_logical_col_width, self._calculate_text_width(logical_col_name, True) + self.padding)
            max_physical_col_width = max(max_physical_col_width, self._calculate_text_width(physical_col_name, False) + self.padding)
            max_type_width = max(max_type_width, self._calculate_text_width(column_type, False) + self.padding)
            max_constraint_width = max(max_constraint_width, self._calculate_text_width(constraint_text, False) + self.padding)
        
        column_total_width = max_logical_col_width + max_physical_col_width + max_type_width + max_constraint_width
        
        return {
            'table_logical_width': logical_table_width,
            'table_physical_width': physical_table_width,
            'table_total_width': table_total_width,
            'logical_width': max_logical_col_width,
            'physical_width': max_physical_col_width,
            'type_width': max_type_width,
            'constraint_width': max_constraint_width,
            'column_total_width': column_total_width,
            'total_width': max(table_total_width, column_total_width)
        }
    
    def render(self, data: Dict[str, Any], x: int, y: int) -> str:
        physical_name = data.get('table_name', 'Table')
        logical_name = data.get('logical_name', physical_name)
        columns = data.get('columns', [])
        
        pk_columns = [col for col in columns if col.get('primary_key', False)]
        regular_columns = [col for col in columns if not col.get('primary_key', False)]
        sorted_columns = pk_columns + regular_columns
        
        widths = self._calculate_widths(data)
        self.width = widths['total_width']
        
        pk_columns_count = len(pk_columns)
        regular_columns_count = len(regular_columns)
        extra_rows = 1 if pk_columns_count > 0 and regular_columns_count == 0 else 0
        actual_height = self.header_height + (len(columns) + extra_rows) * self.row_height
        
        svg_parts = []
        
        svg_parts.append(f'<rect x="{x}" y="{y}" width="{self.width}" height="{actual_height}" '
                        f'fill="white" stroke="black" stroke-width="2"/>')
        
        # ヘッダーセクション（外枠全体の幅に合わせる）
        svg_parts.append(f'<rect x="{x}" y="{y}" width="{self.width}" height="{self.header_height}" '
                        f'fill="#e6f3ff" stroke="black" stroke-width="1"/>')
        
        # テーブル名表示（論理名(物理名)形式）
        table_display = f'{logical_name} ({physical_name})' if logical_name != physical_name else logical_name
        svg_parts.append(f'<text x="{x + 5}" y="{y + self.header_height//2 + 4}" '
                        f'font-family="Arial" font-size="12" font-weight="bold">'
                        f'{table_display}</text>')
        
        current_y = y + self.header_height
        pk_end_y = None
        
        for i, column in enumerate(sorted_columns):
            physical_col_name = column.get('name', f'Column{i}')
            logical_col_name = column.get('logical_name', physical_col_name)
            column_type = column.get('type', 'VARCHAR')
            is_primary = column.get('primary_key', False)
            is_nullable = column.get('nullable', True)
            is_foreign_key = column.get('foreign_key', False)
            
            text_color = "black"
            font_weight = "normal"
            
            constraints = []
            if not is_nullable:
                constraints.append('NOT NULL')
            if is_foreign_key:
                constraints.append('FK')
            constraint_text = ', '.join(constraints) if constraints else ''
            
            # セル位置計算（カラム部分の独立した幅を使用）
            logical_col_x = x
            physical_col_x = x + widths['logical_width']
            type_col_x = x + widths['logical_width'] + widths['physical_width']
            constraint_col_x = x + widths['logical_width'] + widths['physical_width'] + widths['type_width']
            
            # カラムデータ表示
            svg_parts.append(f'<text x="{logical_col_x + 5}" y="{current_y + self.row_height//2 + 3}" '
                            f'font-family="Arial" font-size="10" font-weight="{font_weight}" fill="{text_color}">'
                            f'{logical_col_name}</text>')
            
            svg_parts.append(f'<text x="{physical_col_x + 5}" y="{current_y + self.row_height//2 + 3}" '
                            f'font-family="Arial" font-size="10" fill="black">'
                            f'{physical_col_name}</text>')
            
            svg_parts.append(f'<text x="{type_col_x + 5}" y="{current_y + self.row_height//2 + 3}" '
                            f'font-family="Arial" font-size="9" fill="black">'
                            f'{column_type}</text>')
            
            svg_parts.append(f'<text x="{constraint_col_x + 5}" y="{current_y + self.row_height//2 + 3}" '
                            f'font-family="Arial" font-size="9" fill="black">'
                            f'{constraint_text}</text>')
            
            current_y += self.row_height
            
            if is_primary:
                pk_end_y = current_y
        
        if pk_columns and pk_end_y:
            svg_parts.append(f'<line x1="{x}" y1="{pk_end_y}" x2="{x + widths["column_total_width"]}" y2="{pk_end_y}" '
                            f'stroke="black" stroke-width="1"/>')
        
        # PKのみのテーブルの場合、空行を追加
        if len(pk_columns) > 0 and len(regular_columns) == 0:
            current_y += self.row_height
        
        return '\n'.join(svg_parts)
    
    def calculate_height(self, data: Dict[str, Any]) -> int:
        columns = data.get('columns', [])
        pk_columns = [col for col in columns if col.get('primary_key', False)]
        regular_columns = [col for col in columns if not col.get('primary_key', False)]
        
        # PKのみのテーブルの場合、空行を1行追加
        extra_rows = 1 if len(pk_columns) > 0 and len(regular_columns) == 0 else 0
        return self.header_height + (len(columns) + extra_rows) * self.row_height
    
    def get_width(self, data: Dict[str, Any]) -> int:
        widths = self._calculate_widths(data)
        return widths['total_width']