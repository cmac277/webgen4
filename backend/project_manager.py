"""
Project Manager - Handles file-based project storage and serving
"""
import os
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import signal

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self, base_dir: str = "/app/backend/generated_projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.running_backends = {}  # {session_id: process}
        logger.info(f"ProjectManager initialized with base_dir: {self.base_dir}")
    
    def get_project_dir(self, session_id: str) -> Path:
        """Get the directory path for a project"""
        return self.base_dir / session_id
    
    def create_project_structure(self, session_id: str) -> Dict[str, Path]:
        """Create the directory structure for a project"""
        project_dir = self.get_project_dir(session_id)
        
        # Remove existing project if it exists
        if project_dir.exists():
            logger.info(f"Removing existing project directory: {project_dir}")
            shutil.rmtree(project_dir)
        
        # Create fresh directory structure
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        static_dir = project_dir / "static"
        static_dir.mkdir(exist_ok=True)
        
        backend_dir = project_dir / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        logger.info(f"Created project structure for session {session_id}")
        
        return {
            "root": project_dir,
            "static": static_dir,
            "backend": backend_dir
        }
    
    def save_project_files(
        self,
        session_id: str,
        html_content: str,
        css_content: str,
        js_content: str,
        python_backend: Optional[str] = None,
        requirements_txt: Optional[str] = None,
        package_json: Optional[str] = None,
        readme: Optional[str] = None
    ) -> Dict[str, str]:
        """Save all project files to disk with proper linking"""
        
        dirs = self.create_project_structure(session_id)
        project_dir = dirs["root"]
        static_dir = dirs["static"]
        backend_dir = dirs["backend"]
        
        # Modify HTML to link external CSS and JS files
        html_content_linked = self._link_external_files(html_content, css_content, js_content)
        
        # Save HTML (root level for easy serving)
        html_path = project_dir / "index.html"
        html_path.write_text(html_content_linked, encoding='utf-8')
        logger.info(f"Saved index.html: {html_path}")
        
        # Save CSS
        css_path = static_dir / "styles.css"
        css_path.write_text(css_content, encoding='utf-8')
        logger.info(f"Saved styles.css: {css_path}")
        
        # Save JS
        js_path = static_dir / "app.js"
        js_path.write_text(js_content, encoding='utf-8')
        logger.info(f"Saved app.js: {js_path}")
        
        # Save backend files if provided
        if python_backend:
            backend_path = backend_dir / "server.py"
            backend_path.write_text(python_backend, encoding='utf-8')
            logger.info(f"Saved server.py: {backend_path}")
        
        if requirements_txt:
            req_path = backend_dir / "requirements.txt"
            req_path.write_text(requirements_txt, encoding='utf-8')
            logger.info(f"Saved requirements.txt: {req_path}")
        
        if package_json:
            pkg_path = project_dir / "package.json"
            pkg_path.write_text(package_json, encoding='utf-8')
            logger.info(f"Saved package.json: {pkg_path}")
        
        if readme:
            readme_path = project_dir / "README.md"
            readme_path.write_text(readme, encoding='utf-8')
            logger.info(f"Saved README.md: {readme_path}")
        
        return {
            "html": str(html_path),
            "css": str(css_path),
            "js": str(js_path),
            "backend": str(backend_dir / "server.py") if python_backend else None,
            "requirements": str(backend_dir / "requirements.txt") if requirements_txt else None
        }
    
    def _link_external_files(self, html: str, css: str, js: str) -> str:
        """Modify HTML to link external CSS and JS files properly"""
        import re
        
        # Check if HTML already has embedded styles
        has_embedded_css = "<style>" in html
        has_embedded_js = "<script>" in html and "</script>" in html
        
        # Extract embedded CSS if present and css parameter is empty
        extracted_css = css
        if has_embedded_css and not css.strip():
            # Extract all CSS from style tags
            style_matches = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
            if style_matches:
                extracted_css = '\n\n'.join(style_matches)
                logger.info(f"Extracted {len(extracted_css)} chars of CSS from embedded styles")
        
        # Extract embedded JS if present and js parameter is empty
        extracted_js = js
        if has_embedded_js and not js.strip():
            # Extract all JS from script tags (excluding those with src attribute)
            script_matches = re.findall(r'<script(?![^>]*src=)>(.*?)</script>', html, re.DOTALL)
            if script_matches:
                extracted_js = '\n\n'.join(script_matches)
                logger.info(f"Extracted {len(extracted_js)} chars of JS from embedded scripts")
        
        # Only modify HTML and link external files if we have content to link
        if extracted_css.strip():
            # Remove embedded styles now that we've extracted them
            html = re.sub(r'<style>.*?</style>', '', html, flags=re.DOTALL)
            
            # Add CSS link if not already present
            if '<link rel="stylesheet" href="static/styles.css">' not in html:
                if "</head>" in html:
                    html = html.replace(
                        "</head>",
                        '    <link rel="stylesheet" href="static/styles.css">\n</head>'
                    )
                else:
                    html = html.replace(
                        "<head>",
                        '<head>\n    <link rel="stylesheet" href="static/styles.css">'
                    )
        
        if extracted_js.strip():
            # Remove embedded scripts (but keep CDN scripts with src attribute)
            html = re.sub(r'<script(?![^>]*src=)>.*?</script>', '', html, flags=re.DOTALL)
            
            # Add JS script if not already present
            if '<script src="static/app.js"></script>' not in html:
                if "</body>" in html:
                    html = html.replace(
                        "</body>",
                        '    <script src="static/app.js"></script>\n</body>'
                    )
                else:
                    html += '\n<script src="static/app.js"></script>'
        
        return html, extracted_css, extracted_js
    
    def get_project_files(self, session_id: str) -> Optional[Dict[str, str]]:
        """Get all project file paths"""
        project_dir = self.get_project_dir(session_id)
        
        if not project_dir.exists():
            logger.warning(f"Project directory not found: {project_dir}")
            return None
        
        files = {
            "html": str(project_dir / "index.html"),
            "css": str(project_dir / "static" / "styles.css"),
            "js": str(project_dir / "static" / "app.js"),
            "backend": str(project_dir / "backend" / "server.py"),
            "requirements": str(project_dir / "backend" / "requirements.txt")
        }
        
        # Filter out non-existent files
        return {k: v for k, v in files.items() if Path(v).exists()}
    
    def start_backend(self, session_id: str, port: int = 8002) -> Dict[str, Any]:
        """
        Start the generated backend server for a project
        NOTE: This is a complex operation requiring port management and process isolation
        """
        backend_dir = self.get_project_dir(session_id) / "backend"
        server_path = backend_dir / "server.py"
        
        if not server_path.exists():
            logger.warning(f"No backend file found for session {session_id}")
            return {
                "success": False,
                "message": "No backend file found for this project"
            }
        
        # Check if backend is already running
        if session_id in self.running_backends:
            process = self.running_backends[session_id]
            if process.poll() is None:  # Still running
                logger.info(f"Backend already running for session {session_id}")
                return {
                    "success": True,
                    "message": "Backend already running",
                    "port": port,
                    "url": f"http://localhost:{port}"
                }
        
        try:
            # Install requirements if they exist
            requirements_path = backend_dir / "requirements.txt"
            if requirements_path.exists():
                logger.info(f"Installing requirements for session {session_id}")
                subprocess.run(
                    ["pip", "install", "-r", str(requirements_path)],
                    cwd=str(backend_dir),
                    capture_output=True,
                    timeout=60
                )
            
            # Start the backend server
            logger.info(f"Starting backend server for session {session_id} on port {port}")
            process = subprocess.Popen(
                ["python", "server.py"],
                cwd=str(backend_dir),
                env={**os.environ, "PORT": str(port)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_backends[session_id] = process
            
            return {
                "success": True,
                "message": "Backend started successfully",
                "port": port,
                "url": f"http://localhost:{port}",
                "pid": process.pid
            }
            
        except Exception as e:
            logger.error(f"Failed to start backend for session {session_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to start backend: {str(e)}"
            }
    
    def stop_backend(self, session_id: str) -> Dict[str, Any]:
        """Stop the running backend for a project"""
        if session_id not in self.running_backends:
            return {
                "success": False,
                "message": "No running backend found for this project"
            }
        
        try:
            process = self.running_backends[session_id]
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=5)
            del self.running_backends[session_id]
            
            logger.info(f"Backend stopped for session {session_id}")
            return {
                "success": True,
                "message": "Backend stopped successfully"
            }
        except Exception as e:
            logger.error(f"Failed to stop backend for session {session_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to stop backend: {str(e)}"
            }
    
    def cleanup_project(self, session_id: str):
        """Remove project files and stop backend"""
        # Stop backend if running
        self.stop_backend(session_id)
        
        # Remove project directory
        project_dir = self.get_project_dir(session_id)
        if project_dir.exists():
            shutil.rmtree(project_dir)
            logger.info(f"Cleaned up project for session {session_id}")
