"""
Tools Auto-Discovery — Tự động tìm và load tất cả tools trong thư mục này.

Cách thêm tool mới cho team member:
1. Tạo file .py mới trong thư mục tools/
2. Import decorator: from langchain_core.tools import tool
3. Viết function với @tool decorator
4. Restart server → tool tự động được load

Ví dụ:
    # tools/my_new_tool.py
    from langchain_core.tools import tool
    
    @tool
    def my_tool(query: str) -> str:
        \"\"\"Mô tả tool của bạn.\"\"\"
        return "Kết quả"
"""

from __future__ import annotations
import importlib
import pkgutil
import inspect
from pathlib import Path
from langchain_core.tools import BaseTool


def discover_tools() -> list[BaseTool]:
    """
    Scan tất cả .py files trong thư mục tools/, 
    tìm objects là instance của BaseTool (tức function có @tool decorator).
    
    Returns:
        List các tool objects sẵn sàng bind vào LangGraph agent.
    """
    tools = []
    package_dir = Path(__file__).parent
    
    for module_info in pkgutil.iter_modules([str(package_dir)]):
        if module_info.name.startswith("_"):
            continue
        
        try:
            module = importlib.import_module(f".{module_info.name}", package=__package__)
            
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, BaseTool):
                    tools.append(obj)
                    print(f"  [OK] Loaded tool: {obj.name} (from {module_info.name}.py)")
                    
        except Exception as e:
            print(f"  [WARN] Failed to load {module_info.name}: {e}")
    
    return tools


# Export danh sách tools khi import package
all_tools = discover_tools()
