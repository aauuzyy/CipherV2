"""Constants and configuration for syntax highlighting"""

SYNTAX_COLORS = {
    'keyword': '#569cd6',
    'string': '#ce9178', 
    'comment': '#6a9955',
    'function': '#dcdcaa',
    'number': '#b5cea8',
    'error': '#ff4444'
}

PYTHON_KEYWORDS = [
    'def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for',
    'while', 'return', 'try', 'except', 'finally', 'with', 'as',
    'lambda', 'yield', 'pass', 'break', 'continue', 'True', 'False',
    'None', 'and', 'or', 'not', 'in', 'is', 'async', 'await'
]

CODE_SNIPPETS = {
    "for_loop": "for i in range(10):\n    print(i)",
    "function": "def function_name(param):\n    return param",
    "class": "class ClassName:\n    def __init__(self):\n        pass",
    "try_except": "try:\n    # code\n    pass\nexcept Exception as e:\n    print(e)",
    "file_read": "with open('file.txt', 'r') as f:\n    content = f.read()",
    "list_comp": "[x for x in range(10) if x % 2 == 0]",
    "dict_comp": "{k: v for k, v in enumerate(range(10))}",
    "requests": "import requests\nresponse = requests.get('url')\nprint(response.json())"
}

# Theme configuration
DARK_THEME = {
    'bg_color': "#1e1e1e",
    'secondary_bg': "#2d2d2d",
    'accent_color': "#0d7377",
    'text_color': "#e0e0e0",
    'button_hover': "#14a0a6"
}

LIGHT_THEME = {
    'bg_color': "#f5f5f5",
    'secondary_bg': "#ffffff",
    'accent_color': "#0d7377",
    'text_color': "#000000",
    'button_hover': "#14a0a6"
}