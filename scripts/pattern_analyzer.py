#!/usr/bin/env python3
"""
Pattern Analyzer - Extract patterns from mapped repositories.
Analyzes multiple repo maps to find common patterns and best practices.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class Pattern:
    """A detected code pattern."""
    id: str
    type: str  # naming, architecture, error_handling, testing, config
    name: str
    description: str
    frequency: int = 1
    repos: List[str] = field(default_factory=list)
    examples: List[Dict] = field(default_factory=list)
    confidence: float = 0.5
    category: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class PatternAnalysis:
    """Complete pattern analysis across repos."""
    repos: List[str]
    total_files: int = 0
    total_classes: int = 0
    total_functions: int = 0
    patterns: List[Dict] = field(default_factory=list)
    architecture: Dict = field(default_factory=dict)
    naming: Dict = field(default_factory=dict)
    dependencies: Dict = field(default_factory=dict)
    best_practices: List[Dict] = field(default_factory=list)
    anti_patterns: List[Dict] = field(default_factory=list)


class PatternAnalyzer:
    """Analyze patterns across multiple repositories."""
    
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.repo_data: Dict[str, Dict] = {}
        self.analysis = PatternAnalysis(repos=[])
    
    def load_repo_map(self, repo_map_path: Path) -> Dict:
        """Load a repo map JSON file."""
        with open(repo_map_path) as f:
            data = json.load(f)
        
        repo_name = data.get("name", repo_map_path.stem)
        self.repo_data[repo_name] = data
        self.analysis.repos.append(repo_name)
        self.analysis.total_files += data.get("files", 0)
        self.analysis.total_classes += data.get("stats", {}).get("total_classes", 0)
        self.analysis.total_functions += data.get("stats", {}).get("total_functions", 0)
        
        return data
    
    def analyze_naming_patterns(self):
        """Analyze naming conventions across repos."""
        naming = {
            "snake_case": 0,
            "camelCase": 0,
            "PascalCase": 0,
            "kebab-case": 0,
        }
        
        for repo_name, data in self.repo_data.items():
            for node in data.get("nodes", []):
                name = node.get("name", "")
                if "_" in name and not name[0].isupper():
                    naming["snake_case"] += 1
                elif name[0].islower() and any(c.isupper() for c in name):
                    naming["camelCase"] += 1
                elif name[0].isupper():
                    naming["PascalCase"] += 1
                elif "-" in name:
                    naming["kebab-case"] += 1
        
        self.analysis.naming = naming
        
        # Determine dominant convention
        if naming:
            dominant = max(naming, key=naming.get)
            self._add_pattern(
                type="naming",
                name=f"{dominant}_convention",
                description=f"Dominant naming convention is {dominant}",
                confidence=0.8,
                category="style"
            )
    
    def analyze_architecture_patterns(self):
        """Analyze architectural patterns."""
        architectures = Counter()
        directory_structures = []
        
        for repo_name, data in self.repo_data.items():
            # Analyze directory structure from file paths
            dirs = set()
            for node in data.get("nodes", []):
                file_path = node.get("file", "")
                parts = file_path.split("/")
                if len(parts) > 1:
                    dirs.add(parts[0])
            
            # Detect architecture from top-level directories
            top_dirs = set(d.lower() for d in dirs)
            
            if "src" in top_dirs and ("lib" in top_dirs or "app" in top_dirs):
                architectures["modular"] += 1
            elif "lib" in top_dirs:
                architectures["library"] += 1
            elif "cmd" in top_dirs or "bin" in top_dirs:
                architectures["cli"] += 1
            elif "internal" in top_dirs or "pkg" in top_dirs:
                architectures["go_standard"] += 1
            else:
                architectures["flat"] += 1
            
            directory_structures.append({
                "repo": repo_name,
                "top_dirs": list(dirs)[:10]
            })
        
        self.analysis.architecture = {
            "detected": dict(architectures),
            "structures": directory_structures
        }
        
        # Add dominant architecture as pattern
        if architectures:
            dominant = architectures.most_common(1)[0][0]
            self._add_pattern(
                type="architecture",
                name=f"{dominant}_structure",
                description=f"Dominant architecture pattern is {dominant}",
                confidence=0.7,
                category="structure"
            )
    
    def analyze_class_patterns(self):
        """Analyze class patterns across repos."""
        class_names = []
        method_counts = []
        inheritance_patterns = []
        
        for repo_name, data in self.repo_data.items():
            for node in data.get("nodes", []):
                if node.get("type") == "class":
                    class_names.append(node.get("name", ""))
                    
                    metadata = node.get("metadata", {})
                    methods = metadata.get("methods", [])
                    method_counts.append(len(methods))
                    
                    bases = metadata.get("bases", [])
                    if bases:
                        inheritance_patterns.extend(bases)
        
        # Find common class names
        name_counter = Counter(class_names)
        common_names = name_counter.most_common(10)
        
        # Find common base classes
        base_counter = Counter(inheritance_patterns)
        common_bases = base_counter.most_common(10)
        
        if common_names:
            for name, count in common_names[:3]:
                if count > 1:
                    self._add_pattern(
                        type="naming",
                        name=f"common_class_{name.lower()}",
                        description=f"Common class name: {name} (appears {count} times)",
                        frequency=count,
                        confidence=0.6,
                        category="naming"
                    )
        
        if common_bases:
            for base, count in common_bases[:3]:
                if count > 1:
                    self._add_pattern(
                        type="architecture",
                        name=f"inheritance_{base.lower()}",
                        description=f"Common base class: {base} (used {count} times)",
                        frequency=count,
                        confidence=0.6,
                        category="inheritance"
                    )
        
        self.analysis.best_practices.append({
            "type": "class_stats",
            "avg_methods_per_class": sum(method_counts) / len(method_counts) if method_counts else 0,
            "total_classes": len(class_names)
        })
    
    def analyze_function_patterns(self):
        """Analyze function patterns."""
        function_names = []
        param_counts = []
        
        for repo_name, data in self.repo_data.items():
            for node in data.get("nodes", []):
                if node.get("type") == "function":
                    function_names.append(node.get("name", ""))
                    params = node.get("metadata", {}).get("params", [])
                    param_counts.append(len(params))
        
        # Find common function names
        name_counter = Counter(function_names)
        common_names = name_counter.most_common(10)
        
        for name, count in common_names[:3]:
            if count > 1:
                self._add_pattern(
                    type="naming",
                    name=f"common_function_{name.lower()}",
                    description=f"Common function name: {name} (appears {count} times)",
                    frequency=count,
                    confidence=0.6,
                    category="naming"
                )
        
        self.analysis.best_practices.append({
            "type": "function_stats",
            "avg_params": sum(param_counts) / len(param_counts) if param_counts else 0,
            "total_functions": len(function_names)
        })
    
    def analyze_dependency_patterns(self):
        """Analyze import/dependency patterns."""
        all_imports = []
        import_sources = Counter()
        
        for repo_name, data in self.repo_data.items():
            for node in data.get("nodes", []):
                imports = node.get("imports", [])
                all_imports.extend(imports)
                for imp in imports:
                    # Categorize import
                    if imp.startswith("."):
                        import_sources["relative"] += 1
                    elif imp in ("os", "sys", "json", "re", "pathlib", "typing"):
                        import_sources["stdlib"] += 1
                    else:
                        import_sources["external"] += 1
        
        self.analysis.dependencies = {
            "total_imports": len(all_imports),
            "sources": dict(import_sources)
        }
        
        # Pattern: prefer relative imports
        if import_sources.get("relative", 0) > import_sources.get("external", 0):
            self._add_pattern(
                type="architecture",
                name="relative_imports",
                description="Codebase prefers relative imports",
                confidence=0.7,
                category="imports"
            )
    
    def _add_pattern(self, type: str, name: str, description: str, 
                     frequency: int = 1, confidence: float = 0.5, category: str = ""):
        """Add a pattern to the analysis."""
        pattern_id = f"{type}:{name}"
        
        if pattern_id in self.patterns:
            self.patterns[pattern_id].frequency += frequency
        else:
            self.patterns[pattern_id] = Pattern(
                id=pattern_id,
                type=type,
                name=name,
                description=description,
                frequency=frequency,
                confidence=confidence,
                category=category
            )
    
    def analyze_all(self) -> PatternAnalysis:
        """Run all analyses."""
        print("Analyzing patterns across repos...")
        
        self.analyze_naming_patterns()
        self.analyze_architecture_patterns()
        self.analyze_class_patterns()
        self.analyze_function_patterns()
        self.analyze_dependency_patterns()
        
        # Convert patterns to list
        self.analysis.patterns = [asdict(p) for p in self.patterns.values()]
        
        # Sort by frequency and confidence
        self.analysis.patterns.sort(
            key=lambda x: (x["frequency"], x["confidence"]),
            reverse=True
        )
        
        # Identify anti-patterns
        self._identify_anti_patterns()
        
        return self.analysis
    
    def _identify_anti_patterns(self):
        """Identify potential anti-patterns."""
        for repo_name, data in self.repo_data.items():
            stats = data.get("stats", {})
            
            # Large files
            for node in data.get("nodes", []):
                if node.get("type") == "file":
                    lines = node.get("lines", 0)
                    if lines > 500:
                        self.analysis.anti_patterns.append({
                            "type": "large_file",
                            "file": node.get("name", ""),
                            "repo": repo_name,
                            "lines": lines,
                            "suggestion": "Consider splitting into smaller modules"
                        })
            
            # Too many methods in class
            for node in data.get("nodes", []):
                if node.get("type") == "class":
                    methods = node.get("metadata", {}).get("method_count", 0)
                    if methods > 20:
                        self.analysis.anti_patterns.append({
                            "type": "god_class",
                            "class": node.get("name", ""),
                            "repo": repo_name,
                            "methods": methods,
                            "suggestion": "Consider splitting responsibilities"
                        })


def main():
    parser = argparse.ArgumentParser(description="Analyze patterns across repositories")
    parser.add_argument("repo_maps", nargs="+", help="Paths to repo_map.json files")
    parser.add_argument("-o", "--output", default="pattern_analysis.json", help="Output file")
    
    args = parser.parse_args()
    
    analyzer = PatternAnalyzer()
    
    # Load all repo maps
    for map_path in args.repo_maps:
        path = Path(map_path)
        if not path.exists():
            print(f"Warning: {map_path} not found, skipping")
            continue
        print(f"Loading: {map_path}")
        analyzer.load_repo_map(path)
    
    if not analyzer.repo_data:
        print("Error: No repo maps loaded")
        sys.exit(1)
    
    # Analyze
    analysis = analyzer.analyze_all()
    
    # Save results
    output_data = asdict(analysis)
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nAnalysis complete:")
    print(f"  Repos: {len(analysis.repos)}")
    print(f"  Files: {analysis.total_files}")
    print(f"  Classes: {analysis.total_classes}")
    print(f"  Functions: {analysis.total_functions}")
    print(f"  Patterns found: {len(analysis.patterns)}")
    print(f"  Anti-patterns: {len(analysis.anti_patterns)}")
    print(f"  Output: {args.output}")
    
    # Also output to stdout
    print(json.dumps(output_data))


if __name__ == "__main__":
    main()
