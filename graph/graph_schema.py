from enum import Enum
import sqlite3
import sqlite3

class NodeType(str, Enum):
    REPOSITORY = "repository"
    MODULE = "module"
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    TEST = "test"
    EXTERNAL_LIBRARY = "external_library"
    EXTERNAL_SERVICE = "external_service"

class EdgeType(str, Enum):
    CONTAINS = "contains"
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    TESTS = "tests"