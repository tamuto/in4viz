import sys
import importlib.util
from pathlib import Path

# plan1のmodels.pyを直接インポート
models_path = Path(__file__).parent.parent.parent / 'planning' / 'in4viz' / 'models.py'
spec = importlib.util.spec_from_file_location("planning_models", models_path)
planning_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planning_models)

# モデルクラスを取得
Table = planning_models.Table
Column = planning_models.Column
LineType = planning_models.LineType
Cardinality = planning_models.Cardinality

# plan2のクラスをインポート
from .er_diagram import ERDiagram
from .drawio_stencil import DrawioTableStencil

__all__ = ['ERDiagram', 'Table', 'Column', 'LineType', 'Cardinality', 'DrawioTableStencil']

__version__ = "0.1.0"
