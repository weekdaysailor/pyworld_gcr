"""Simple HTTP server for serving World3 visualization files."""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import socket
import sys

class WorldVizHandler(SimpleHTTPRequestHandler):
    """Custom handler that serves files from the output directory."""

    def translate_path(self, path):
        """Translate URL paths to local filesystem paths."""
        # Strip query parameters and fragments
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = path.strip('/')

        # Define the base output directory
        output_dir = "myworld3/output"

        # If it's an HTML file request
        if path.endswith('.html'):
            # First try the exact path
            exact_path = os.path.join(output_dir, path)
            if os.path.exists(exact_path):
                print(f"Serving file: {exact_path}")
                return exact_path

            # Try with _new suffix as fallback
            base, ext = os.path.splitext(path)
            new_path = os.path.join(output_dir, f"{base}_new{ext}")
            if os.path.exists(new_path):
                print(f"Serving file: {new_path}")
                return new_path

            print(f"File not found: Tried {exact_path} and {new_path}")
            return exact_path  # Return original path for 404 handling

        # For non-HTML files
        return os.path.join(output_dir, path)

    def do_GET(self):
        """Handle GET requests with detailed logging."""
        print(f"\nReceived request for: {self.path}")
        file_path = self.translate_path(self.path)
        print(f"Translated to file path: {file_path}")
        return super().do_GET()

def find_free_port(start_port=8081, max_tries=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_tries - 1}")

def run_server(port=None):
    """Run the HTTP server."""
    if port is None:
        port = find_free_port()

    # Ensure output directory exists
    os.makedirs("myworld3/output", exist_ok=True)

    try:
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, WorldVizHandler)
        print(f"\nServing World3 visualizations at http://0.0.0.0:{port}")
        print("\nAvailable visualizations:")
        print("- /population_comparison.html")
        print("- /industrial_output_comparison.html")
        print("- /pollution_comparison.html")
        print("\nPress Ctrl+C to stop the server\n")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server()