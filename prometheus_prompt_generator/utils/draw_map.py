import os
import pathlib
from gitignore_parser import parse_gitignore
from typing import List, Dict, Set
from html import escape
import time
import json

class ProjectMapper:
    FILE_ICONS: Dict[str, str] = {
        '.py': 'https://www.python.org/static/favicon.ico',
        '.js': 'https://raw.githubusercontent.com/voodootikigod/logo.js/master/js.png',
        '.ts': 'https://www.typescriptlang.org/favicon-32x32.png',
        '.java': 'https://www.java.com/favicon.ico',
        '.cpp': 'https://isocpp.org/favicon.ico',
        '.c': 'https://isocpp.org/favicon.ico',
        '.h': 'https://isocpp.org/favicon.ico',
        '.cs': 'https://learn.microsoft.com/favicon.ico',
        '.go': 'https://go.dev/favicon.ico',
        '.rb': 'https://www.ruby-lang.org/favicon.ico',
        '.php': 'https://www.php.net/favicon.ico',
        '.html': 'https://www.w3.org/favicon.ico',
        '.css': 'https://www.w3.org/Style/CSS/logo-2012.ico',
        '.md': 'https://markdown-here.com/img/favicon.ico',
        '.txt': 'https://cdn-icons-png.flaticon.com/512/337/337946.png',
        '.json': 'https://json.org/favicon.ico',
        '.yml': 'https://yaml.org/favicon.ico',
        '.yaml': 'https://yaml.org/favicon.ico',
        '.sh': 'https://cdn-icons-png.flaticon.com/512/7192/719282.png',
        '.rs': 'https://www.rust-lang.org/static/images/favicon-32x32.png',
        '.sql': 'https://cdn-icons-png.flaticon.com/512/4299/4299956.png',
        '.png': 'https://cdn-icons-png.flaticon.com/512/337/337948.png',
        '.jpg': 'https://cdn-icons-png.flaticon.com/512/337/337940.png',
        '.jpeg': 'https://cdn-icons-png.flaticon.com/512/337/337940.png',
        '.gif': 'https://cdn-icons-png.flaticon.com/512/337/337936.png',
    }

    def __init__(self, root_dir: str):
        self.root_dir = pathlib.Path(root_dir).resolve()
        self.gitignore_matcher = self._load_gitignore()
        self.output_file = self.root_dir / "project_map.html"
        print(f"Output file set to: {self.output_file}")

    def _load_gitignore(self) -> callable:
        """Load and parse .gitignore patterns from the root directory."""
        gitignore_path = self.root_dir / ".gitignore"

        def default_matcher(path: str) -> bool:
            return False

        matcher = default_matcher

        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    gitignore_content = f.read().strip()
                    print(f".gitignore contents:\n{gitignore_content}")
                matcher = parse_gitignore(str(gitignore_path))
            except Exception as e:
                print(f"Warning: Could not parse .gitignore: {e}")

        default_ignores = {
            '.git/', '__pycache__/', '*.pyc', '*.egg-info/',
            'venv/', '.venv/', 'node_modules/', 'dist/', 'build/'
        }

        original_matcher = matcher

        def combined_matcher(path: str) -> bool:
            normalized_path = path.replace(os.sep, '/')
            if original_matcher(normalized_path):
                print(f"Ignoring via .gitignore: {path} (normalized: {normalized_path})")
                return True

            path_obj = pathlib.Path(path)
            for ignore in default_ignores:
                if '*' in ignore:
                    if path_obj.match(ignore.replace('/', os.sep)):
                        print(f"Ignoring via default: {path} (matches {ignore})")
                        return True
                else:
                    ignore_clean = ignore.rstrip('/')
                    if any(part == ignore_clean for part in path_obj.parts):
                        print(f"Ignoring via default: {path} (matches {ignore})")
                        return True
            return False

        return combined_matcher

    def _should_ignore(self, path: pathlib.Path, visited: Set[pathlib.Path]) -> bool:
        """Check if a path should be ignored based on gitignore patterns."""
        try:
            resolved_path = path.resolve()
        except Exception as e:
            print(f"Failed to resolve path {path}: {e}")
            return True

        if resolved_path in visited:
            print(f"Skipping already visited path: {path}")
            return True
        visited.add(resolved_path)

        try:
            relative_path = str(path.relative_to(self.root_dir)).replace(os.sep, '/')
            print(f"Checking path: {path} (relative: {relative_path})")
        except ValueError:
            print(f"Path {path} is not a subpath of {self.root_dir}, using full path")
            relative_path = str(path).replace(os.sep, '/')

        return self.gitignore_matcher(relative_path)

    def _get_file_icon(self, path: pathlib.Path) -> str:
        """Get appropriate logo URL based on file extension."""
        if path.is_dir():
            return 'https://cdn-icons-png.flaticon.com/512/7153/715399.png'
        ext = path.suffix.lower()
        return self.FILE_ICONS.get(ext, 'https://cdn-icons-png.flaticon.com/512/1375/1375106.png')

    def _generate_tree_data(self, path: pathlib.Path, parent_id: str = "#", visited: Set[pathlib.Path] = None) -> List[Dict]:
        """Generate JSON data for jsTree recursively."""
        if visited is None:
            visited = set()

        if self._should_ignore(path, visited):
            print(f"Path ignored: {path}")
            return []

        node_id = f"node-{hash(str(path))}"
        name = path.name
        icon = self._get_file_icon(path)

        data = []
        if path.is_dir():
            node = {
                "id": node_id,
                "parent": parent_id,
                "text": name + "/",
                "type": "folder",
                "state": {"opened": True},
                "icon": icon,
                "children": []
            }
            try:
                children = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                for child in children:
                    child_data = self._generate_tree_data(child, node_id, visited)
                    # Filter out invalid child data
                    if child_data:
                        valid_children = [child_node for child_node in child_data if child_node and isinstance(child_node, dict) and "id" in child_node]
                        node["children"].extend(valid_children)
                # Only add the node if it has valid data
                if node["id"]:
                    data.append(node)
                else:
                    print(f"Skipping node with invalid id: {path}")
            except PermissionError as e:
                print(f"Permission denied for {path}: {e}")
                # Skip adding this node if permission is denied
        else:
            file_node = {
                "id": node_id,
                "parent": parent_id,
                "text": name,
                "type": "file",
                "icon": icon
            }
            if file_node["id"]:
                data.append(file_node)
            else:
                print(f"Skipping file node with invalid id: {path}")

        return data

    def _generate_ai_readable_text(self, path: pathlib.Path, prefix: str = "", is_last: bool = True, visited: Set[pathlib.Path] = None) -> List[str]:
        """Generate AI-readable text with [DIR] and [FILE] tags."""
        if visited is None:
            visited = set()

        lines = []

        if self._should_ignore(path, visited):
            return lines

        connector = "└── " if is_last else "├── "
        if path.is_dir():
            lines.append(f"{prefix}{connector}[DIR] {path.name}/")
            try:
                children = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                new_prefix = prefix + ("    " if is_last else "│   ")
                for i, child in enumerate(children):
                    lines.extend(self._generate_ai_readable_text(child, new_prefix, i == len(children) - 1, visited))
            except PermissionError:
                print(f"Permission denied for {path}")
        else:
            lines.append(f"{prefix}{connector}[FILE] {path.name}")

        return lines

    def create_project_map(self):
        """Create an interactive jsTree-based project map using local files."""
        try:
            # Verify local files exist and print their paths for debugging
            lib_dir = self.root_dir / "lib"
            theme_dir = lib_dir / "themes" / "default"
            required_files = [
                theme_dir / "style.min.css",
                lib_dir / "jquery-3.7.1.min.js",
                lib_dir / "jstree.min.js",
                theme_dir / "throbber.gif"
            ]
            for file in required_files:
                if not file.exists():
                    raise FileNotFoundError(f"Required file not found: {file}. Please ensure it is in {file.parent}.")
                print(f"Verified file exists: {file}")

            # Generate tree data for visualization
            visited = set()
            tree_data = self._generate_tree_data(self.root_dir, visited=visited)
            print(f"Tree data: {json.dumps(tree_data, indent=2)}")
            if not tree_data:
                print("Warning: No tree data generated. Check if all paths are being ignored.")

            # Generate AI-readable text for clipboard
            visited.clear()  # Reset visited set for text generation
            ai_readable_text = "\n".join(self._generate_ai_readable_text(self.root_dir, visited=visited))

            creation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.root_dir.stat().st_ctime))

            # Debug: Print the current working directory and output file path
            print(f"Current working directory: {os.getcwd()}")
            print(f"Writing to: {self.output_file.absolute()}")

            # HTML template using relative paths to local files
            html_base = (
                "<!DOCTYPE html><html><head><title>Project Structure Map</title>"
                '<link rel="stylesheet" href="lib/themes/default/style.min.css" />'
                "<style>body{{font-family:'Segoe UI',Arial,sans-serif;background-color:#1e1e1e;color:#ffffff;margin:0;padding:20px;}}.container{{max-width:800px;margin:0 auto;background:#252526;padding:20px;border-radius:8px;box-shadow:0 4px 6px rgba(0,0,0,0.1);}}h1{{color:#ffffff;margin-top:0;font-size:24px;}}p{{color:#cccccc;margin:5px 0;}}hr{{border:none;border-top:1px solid #3f3f3f;margin:20px 0;}}button{{background-color:#007acc;color:#ffffff;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;font-size:14px;transition:background-color 0.2s;margin-bottom:10px;}}button:hover{{background-color:#0061a8;}}#tree{{padding:10px;}}.jstree-default .jstree-themeicon{{margin-right:4px;}}.jstree-default .jstree-anchor{{color:#ffffff;padding:2px 8px;}}.jstree-default .jstree-hovered{{background-color:#333333;border-radius:4px;}}.jstree-default .jstree-clicked{{background-color:#005ba1;border-radius:4px;}}.error-message{{color:#ff5555;font-style:italic;}}</style>"
                "</head><body><div class='container'><button onclick='copyToClipboard()'>Copy to Clipboard</button><h1>Project Structure Map</h1>"
                "<p>Generated on: {creation_time}</p><p>Root: {root_dir}</p><hr><div id='tree'></div></div>"
                '<script src="lib/jquery-3.7.1.min.js"></script>'
                '<script src="lib/jstree.min.js"></script>'
                "<script>$(document).ready(function(){{if(typeof $==='undefined'||typeof $.jstree==='undefined'){{$(\"#tree\").html(\"<p class='error-message'>Failed to load jQuery or jsTree. Check browser console for errors.</p>\");console.error('jQuery or jsTree failed to load');return;}}try{{const treeData={tree_data_json};if(!treeData||treeData.length===0){{$(\"#tree\").html(\"<p class='error-message'>No files or directories to display. Check if your .gitignore or ignore patterns are excluding everything.</p>\");return;}}$(\"#tree\").jstree({{'core':{{'data':treeData,'check_callback':true,'themes':{{'name':'default','dots':false,'icons':true}}}},'types':{{'folder':{{}},'file':{{}}}},'plugins':['types']}});}}catch(e){{$(\"#tree\").html(\"<p class='error-message'>Error rendering tree: \"+e.message+\"</p>\");console.error('jsTree error:',e);}}}});function copyToClipboard(){{const text=`{ai_readable_text_escaped}`;navigator.clipboard.writeText(text).then(() => {{alert('Project structure copied to clipboard!');}},(err) => {{alert('Failed to copy: '+err);}});}}</script>"
                "</body></html>"
            )

            # Format the HTML with dynamic content
            html_content = html_base.format(
                creation_time=creation_time,
                root_dir=escape(str(self.root_dir)),
                tree_data_json=json.dumps(tree_data, ensure_ascii=False),
                ai_readable_text_escaped=escape(ai_readable_text)
            )

            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"Project map successfully created at: {self.output_file}")

        except Exception as e:
            print(f"Error creating project map: {e}")
            raise

def main():
    current_dir = os.getcwd()
    mapper = ProjectMapper(current_dir)
    mapper.create_project_map()

if __name__ == "__main__":
    main()