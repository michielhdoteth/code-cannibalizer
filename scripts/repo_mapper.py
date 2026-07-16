#!/usr/bin/env python3
"""
Repo Mapper - Map repository structure using AST parsing.
Creates a JSON graph of files, classes, functions, and relationships.
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict


# Language detection by extension
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c_header",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
}

# Default ignore patterns
DEFAULT_IGNORE = [
    "**/.git/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/dist/**",
    "**/build/**",
    "**/*.pyc",
    "**/.DS_Store",
    "**/Thumbs.db",
]


@dataclass
class CodeNode:
    """A node in the code graph."""
    id: str
    type: str  # file, class, function, method, variable, import
    name: str
    file: str
    line: int = 0
    end_line: int = 0
    language: str = ""
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    complexity: int = 1
    lines: int = 0
    metadata: Dict = field(default_factory=dict)


@dataclass
class CodeEdge:
    """An edge in the code graph."""
    source: str
    target: str
    type: str  # imports, calls, inherits, implements, uses
    metadata: Dict = field(default_factory=dict)


@dataclass
class RepoMap:
    """Complete repository map."""
    name: str
    root: str
    language: str = ""
    files: int = 0
    nodes: List[Dict] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)
    languages_detected: Dict = field(default_factory=dict)


class RepoMapper:
    """Map a repository's structure using AST parsing."""
    
    def __init__(self, root: Path, ignore_patterns: List[str] = None):
        self.root = root
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: List[CodeEdge] = []
        self.stats = {
            "files_scanned": 0,
            "files_skipped": 0,
            "languages": {},
            "total_classes": 0,
            "total_functions": 0,
            "total_lines": 0,
        }
    
    def should_ignore(self, path: Path) -> bool:
        """Check if path matches any ignore pattern."""
        from fnmatch import fnmatch
        rel_path = str(path.relative_to(self.root))
        for pattern in self.ignore_patterns:
            if fnmatch(rel_path, pattern) or fnmatch(f"**/{rel_path}", pattern):
                return True
        return False
    
    def detect_language(self, path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        return LANGUAGE_MAP.get(path.suffix.lower())
    
    def generate_id(self, file: str, name: str, type: str) -> str:
        """Generate a unique node ID."""
        return f"{type}:{file}:{name}"
    
    def map_python_file(self, path: Path) -> List[CodeNode]:
        """Map a Python file using AST."""
        nodes = []
        rel_path = str(path.relative_to(self.root))
        
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
            
            # File node
            file_id = f"file:{rel_path}:"
            file_node = CodeNode(
                id=file_id,
                type="file",
                name=rel_path,
                file=rel_path,
                language="python",
                lines=len(content.split('\n')),
                metadata={"size": len(content)}
            )
            nodes.append(file_node)
            self.stats["total_lines"] += file_node.lines
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            file_node.imports = imports
            
            # Extract classes and functions at module level
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_node = self._extract_python_class(node, rel_path, file_id)
                    nodes.append(class_node)
                    file_node.children.append(class_node.id)
                    self.stats["total_classes"] += 1
                    
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_node = self._extract_python_function(node, rel_path, file_id)
                    nodes.append(func_node)
                    file_node.children.append(func_node.id)
                    self.stats["total_functions"] += 1
            
            self.stats["files_scanned"] += 1
            self.stats["languages"]["python"] = self.stats["languages"].get("python", 0) + 1
            
        except Exception as e:
            print(f"  Warning: Could not parse {rel_path}: {e}")
            self.stats["files_skipped"] += 1
        
        return nodes
    
    def _extract_python_class(self, node: ast.ClassDef, file: str, parent_id: str) -> CodeNode:
        """Extract a Python class."""
        # Get bases
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.unparse(base))
        
        # Get decorators
        decorators = [ast.unparse(dec) for dec in node.decorator_list]
        
        # Get docstring
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) 
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value[:200]
        
        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
        
        class_id = self.generate_id(file, node.name, "class")
        
        return CodeNode(
            id=class_id,
            type="class",
            name=node.name,
            file=file,
            line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            language="python",
            parent=parent_id,
            decorators=decorators,
            docstring=docstring,
            metadata={
                "bases": bases,
                "methods": methods,
                "method_count": len(methods)
            }
        )
    
    def _extract_python_function(self, node, file: str, parent_id: str) -> CodeNode:
        """Extract a Python function."""
        # Get decorators
        decorators = [ast.unparse(dec) for dec in node.decorator_list]
        
        # Get docstring
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value[:200]
        
        # Get return type
        returns = ast.unparse(node.returns) if node.returns else None
        
        # Get parameters
        params = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        func_id = self.generate_id(file, node.name, "function")
        
        return CodeNode(
            id=func_id,
            type="function",
            name=node.name,
            file=file,
            line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            language="python",
            parent=parent_id,
            decorators=decorators,
            docstring=docstring,
            metadata={
                "params": params,
                "returns": returns,
                "is_async": isinstance(node, ast.AsyncFunctionDef)
            }
        )
    
    def map_js_ts_file(self, path: Path) -> List[CodeNode]:
        """Map a JavaScript/TypeScript file using regex."""
        nodes = []
        rel_path = str(path.relative_to(self.root))
        
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            lang = "typescript" if path.suffix in ('.ts', '.tsx') else "javascript"
            
            # File node
            file_id = f"file:{rel_path}:"
            file_node = CodeNode(
                id=file_id,
                type="file",
                name=rel_path,
                file=rel_path,
                language=lang,
                lines=len(content.split('\n')),
                metadata={"size": len(content)}
            )
            nodes.append(file_node)
            self.stats["total_lines"] += file_node.lines
            
            # Extract imports
            imports = re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", content)
            imports += re.findall(r"require\s*\(\s*['\"]([^'\"]+)['\"]", content)
            file_node.imports = imports
            
            # Extract exports
            exports = re.findall(r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)", content)
            file_node.exports = exports
            
            # Extract classes
            for match in re.finditer(r"export\s+class\s+(\w+)(?:\s+extends\s+(\w+))?", content):
                class_name = match.group(1)
                extends = match.group(2)
                line_num = content[:match.start()].count('\n') + 1
                
                class_id = self.generate_id(rel_path, class_name, "class")
                class_node = CodeNode(
                    id=class_id,
                    type="class",
                    name=class_name,
                    file=rel_path,
                    line=line_num,
                    language=lang,
                    parent=file_id,
                    metadata={"extends": extends}
                )
                nodes.append(class_node)
                file_node.children.append(class_id)
                self.stats["total_classes"] += 1
            
            # Extract functions
            for match in re.finditer(r"export\s+(?:async\s+)?function\s+(\w+)", content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                func_id = self.generate_id(rel_path, func_name, "function")
                func_node = CodeNode(
                    id=func_id,
                    type="function",
                    name=func_name,
                    file=rel_path,
                    line=line_num,
                    language=lang,
                    parent=file_id,
                    metadata={"is_async": "async" in content[match.start():match.end()+20]}
                )
                nodes.append(func_node)
                file_node.children.append(func_id)
                self.stats["total_functions"] += 1
            
            self.stats["files_scanned"] += 1
            self.stats["languages"][lang] = self.stats["languages"].get(lang, 0) + 1
            
        except Exception as e:
            print(f"  Warning: Could not parse {rel_path}: {e}")
            self.stats["files_skipped"] += 1
        
        return nodes
    
    def map_file(self, path: Path) -> List[CodeNode]:
        """Map a single file based on language."""
        lang = self.detect_language(path)
        
        if lang == "python":
            return self.map_python_file(path)
        elif lang in ("javascript", "typescript"):
            return self.map_js_ts_file(path)
        else:
            return []
    
    def map_directory(self) -> RepoMap:
        """Map the entire directory."""
        print(f"Mapping: {self.root}")
        
        # Process all files
        for file_path in sorted(self.root.rglob('*')):
            if not file_path.is_file():
                continue
            if self.should_ignore(file_path):
                self.stats["files_skipped"] += 1
                continue
            
            nodes = self.map_file(file_path)
            for node in nodes:
                self.nodes[node.id] = node
        
        # Build edges from imports
        self._build_import_edges()
        
        # Determine primary language
        if self.stats["languages"]:
            primary_lang = max(self.stats["languages"], key=self.stats["languages"].get)
        else:
            primary_lang = "unknown"
        
        # Build repo map
        repo_map = RepoMap(
            name=self.root.name,
            root=str(self.root),
            language=primary_lang,
            files=self.stats["files_scanned"],
            nodes=[asdict(n) for n in self.nodes.values()],
            edges=[asdict(e) for e in self.edges],
            stats=self.stats,
            languages_detected=self.stats["languages"]
        )
        
        return repo_map
    
    def _build_import_edges(self):
        """Build edges from import relationships."""
        # Create a lookup of module names to node IDs
        module_to_node = {}
        for node in self.nodes.values():
            if node.type in ("file", "class", "function"):
                # Extract module name from file path
                module = node.file.replace('/', '.').replace('\\', '.')
                if module.endswith('.py'):
                    module = module[:-3]
                elif module.endswith(('.js', '.ts', '.jsx', '.tsx')):
                    module = module.rsplit('.', 1)[0]
                module_to_node[module] = node.id
        
        # Build import edges
        for node in self.nodes.values():
            if node.type == "file":
                for imp in node.imports:
                    # Try to find matching module
                    for module, target_id in module_to_node.items():
                        if imp in module or module in imp:
                            self.edges.append(CodeEdge(
                                source=node.id,
                                target=target_id,
                                type="imports"
                            ))


def main():
    parser = argparse.ArgumentParser(description="Map repository structure")
    parser.add_argument("repo_path", help="Path to repository to map")
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("--ignore", action="append", default=[], help="Additional ignore patterns")
    
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        print(f"Error: Path not found: {repo_path}")
        sys.exit(1)
    
    ignore_patterns = DEFAULT_IGNORE + args.ignore
    mapper = RepoMapper(repo_path, ignore_patterns)
    repo_map = mapper.map_directory()
    
    # Output
    output_data = asdict(repo_map)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = repo_path / "repo_map.json"
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nMapping complete:")
    print(f"  Files: {repo_map.files}")
    print(f"  Classes: {repo_map.stats['total_classes']}")
    print(f"  Functions: {repo_map.stats['total_functions']}")
    print(f"  Lines: {repo_map.stats['total_lines']}")
    print(f"  Languages: {repo_map.languages_detected}")
    print(f"  Output: {output_path}")
    
    # Also output to stdout for pipeline
    print(json.dumps(output_data))


if __name__ == "__main__":
    main()
