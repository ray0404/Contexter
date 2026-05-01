import http.server
import socketserver
import os
import markdown
import re
from pygments.formatters import HtmlFormatter

PORT = 8000
WIKI_DIR = "deepwiki"

# Ensure the directory exists
if not os.path.exists(WIKI_DIR):
    print(f"Error: Directory '{WIKI_DIR}' not found.")
    exit(1)

STYLE = """
<style>
    body {
        font-family: 'Roboto', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
    }
    .container {
        background: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 { color: #2c3e50; }
    a { color: #3498db; text-decoration: none; }
    a:hover { text-decoration: underline; }
    pre {
        background: #f8f8f8;
        padding: 15px;
        border-radius: 4px;
        overflow-x: auto;
        border: 1px solid #ddd;
    }
    code { font-family: 'Consolas', 'Monaco', monospace; }
    .back-link { margin-bottom: 20px; display: inline-block; }
    ul { list-style-type: none; padding: 0; }
    li { margin-bottom: 10px; padding: 10px; border-bottom: 1px solid #eee; }
    li:last-child { border-bottom: none; }
</style>
"""

class WikiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Generate index by walking the directory
            links = []
            for root, dirs, files in os.walk(WIKI_DIR):
                for f in sorted(files):
                    if f.lower().endswith(".md"):
                        # Rel path from WIKI_DIR
                        abs_path = os.path.join(root, f)
                        rel_path = os.path.relpath(abs_path, WIKI_DIR)
                        # Remove .md for the link url (ensure only at the end)
                        url_stub = rel_path[:-3] if rel_path.lower().endswith(".md") else rel_path
                        # Use forward slashes for URL
                        url_path = "/" + url_stub.replace(os.sep, "/")
                        display_name = url_stub.replace(os.sep, "/")
                        links.append(f'<li><a href="{url_path}">{display_name}</a></li>')
            
            links_html = "".join(links)
            
            html = f"""
            <html>
            <head><title>DeepWiki Contexter</title>{STYLE}</head>
            <body>
                <div class="container">
                    <h1>Contexter Documentation</h1>
                    <ul>{links_html}</ul>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            return

        # Handle file requests
        # Clean path
        path = self.path.lstrip("/")
        filepath = os.path.join(WIKI_DIR, path)
        
        # Try finding the file. It might lack .md extension in the URL
        found_path = None
        if os.path.exists(filepath) and os.path.isfile(filepath):
            found_path = filepath
        elif os.path.exists(filepath + ".md"):
            found_path = filepath + ".md"
            
        if found_path and found_path.endswith(".md"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open(found_path, "r", encoding="utf-8") as f:
                content = f.read()
                html_content = markdown.markdown(content, extensions=['fenced_code', 'codehilite', 'tables'])
                
                # Post-processing to fix relative links in <a> tags
                def fix_link(match):
                    href = match.group(1)
                    # Skip absolute links, mailto, protocol-relative, and fragments
                    if not href.startswith(('http://', 'https://', 'mailto:', '#', '//')):
                        # Strip .md extension before any # or ? or at end of string, case-insensitive
                        href = re.sub(r'\.md(?=[#?]|$)', '', href, flags=re.IGNORECASE)
                    return f'href="{href}"'

                def fix_tag(match):
                    tag = match.group(0)
                    return re.sub(r'href="([^"]+)"', fix_link, tag)

                html_content = re.sub(r'<a\s+[^>]+>', fix_tag, html_content, flags=re.IGNORECASE)

            full_html = f"""
            <html>
            <head><title>{path}</title>{STYLE}</head>
            <body>
                <div class="container">
                    <a href="/" class="back-link">← Back to Index</a>
                    {html_content}
                </div>
            </body>
            </html>
            """
            self.wfile.write(full_html.encode("utf-8"))
            return
            
        # Fallback to default handler for static assets if any
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WikiHandler) as httpd:
        print(f"Serving Wiki at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()