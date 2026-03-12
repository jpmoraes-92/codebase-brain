import os

class LanguageDetector:
    EXT_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".java": "java",
        ".go": "go"
    }

    @classmethod
    def detect(cls, filepath: str) -> str:
        _, ext = os.path.splitext(filepath)
        return cls.EXT_MAP.get(ext.lower(), "unknown")