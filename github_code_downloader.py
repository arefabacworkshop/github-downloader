import os
import requests
import base64
from urllib.parse import quote_plus
import json

class GitHubCodeDownloader:
    """GitHub Code Downloader - Search and download code matching search queries"""
    
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            
    def search_code(self, query, language=None, max_results=30):
        """Search for code matching query and optional language filter"""
        search_query = quote_plus(query)
        if language:
            search_query += f"+language:{language}"
            
        url = f"{self.base_url}/search/code?q={search_query}&per_page={max_results}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error searching GitHub: {response.status_code}")
            print(response.json().get('message', 'Unknown error'))
            return []
            
        results = response.json()
        return results.get('items', [])
    
    def get_file_content(self, repo, path):
        """Get content of a specific file from GitHub"""
        url = f"{self.base_url}/repos/{repo}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error getting file content: {response.status_code}")
            return None
            
        content = response.json()
        if content.get('encoding') == 'base64':
            return base64.b64decode(content.get('content')).decode('utf-8')
        return None
    
    def download_file(self, repo, path, destination_folder):
        """Download a file from GitHub to local destination"""
        content = self.get_file_content(repo, path)
        if not content:
            return False
            
        # Create destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)
        
        # Extract filename from path and create full destination path
        filename = os.path.basename(path)
        repo_folder = repo.replace('/', '_')
        full_destination = os.path.join(destination_folder, repo_folder)
        os.makedirs(full_destination, exist_ok=True)
        
        file_path = os.path.join(full_destination, filename)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True

def main():
    # Check for GitHub token in environment variable
    token = os.environ.get('GITHUB_TOKEN')
    
    print("GitHub Code Downloader")
    print("=====================")
    
    if not token:
        print("Warning: No GitHub token found. API rate limits will be restricted.")
        print("Set GITHUB_TOKEN environment variable for better results.")
    
    downloader = GitHubCodeDownloader(token)
    
    while True:
        print("\n1. Search and download code")
        print("2. Exit")
        choice = input("\nChoose an option: ")
        
        if choice == '2':
            break
            
        if choice == '1':
            query = input("Enter search query: ")
            language = input("Filter by language (optional, press Enter to skip): ")
            
            if not language:
                language = None
                
            print(f"Searching for '{query}'...")
            results = downloader.search_code(query, language)
            
            if not results:
                print("No results found.")
                continue
                
            print(f"Found {len(results)} matching files.")
            
            for i, item in enumerate(results):
                repo = item['repository']['full_name']
                path = item['path']
                print(f"{i+1}. {repo}/{path}")
            
            selection = input("\nEnter numbers to download (comma-separated) or 'all': ")
            
            indices = []
            if selection.lower() == 'all':
                indices = range(len(results))
            else:
                try:
                    indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                except ValueError:
                    print("Invalid selection.")
                    continue
            
            download_dir = "github_downloads"
            for idx in indices:
                if 0 <= idx < len(results):
                    item = results[idx]
                    repo = item['repository']['full_name']
                    path = item['path']
                    print(f"Downloading {repo}/{path}...")
                    
                    if downloader.download_file(repo, path, download_dir):
                        print(f"Successfully downloaded to {download_dir}/{repo.replace('/', '_')}/{os.path.basename(path)}")
                    else:
                        print(f"Failed to download {repo}/{path}")
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()