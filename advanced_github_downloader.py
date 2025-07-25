import os
import requests
import base64
import re
from urllib.parse import quote_plus
import json
import argparse
from concurrent.futures import ThreadPoolExecutor

class GitHubCodeDownloader:
    """Advanced GitHub Code Downloader with search validation and parallel downloads"""
    
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            
    def search_code(self, query, language=None, max_results=100):
        """Search for code matching query and optional language filter with pagination support"""
        search_query = quote_plus(query)
        if language:
            search_query += f"+language:{language}"
        
        # Calculate how many pages we need
        per_page = 100  # GitHub API maximum per page
        pages_needed = (max_results + per_page - 1) // per_page
        
        all_results = []
        
        for page in range(1, pages_needed + 1):
            print(f"Fetching page {page} of {pages_needed}...")
            
            url = f"{self.base_url}/search/code?q={search_query}&per_page={per_page}&page={page}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Error searching GitHub: {response.status_code}")
                print(response.json().get('message', 'Unknown error'))
                break
                
            results = response.json()
            items = results.get('items', [])
            
            if not items:
                print(f"No more results found on page {page}.")
                break
                
            all_results.extend(items)
            
            # Check if we've reached our desired max_results
            if len(all_results) >= max_results:
                all_results = all_results[:max_results]
                break
                
            # GitHub API has rate limits - add a small delay between requests
            if page < pages_needed:
                import time
                time.sleep(0.5)  # 500ms delay between requests
        
        print(f"Found a total of {len(all_results)} results.")
        return all_results
    
    def get_file_content(self, repo, path):
        """Get content of a specific file from GitHub"""
        url = f"{self.base_url}/repos/{repo}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error getting file content: {response.status_code}")
            return None
            
        content = response.json()
        if content.get('encoding') == 'base64':
            return base64.b64decode(content.get('content')).decode('utf-8', errors='replace')
        return None
    
    def validate_file_content(self, content, validation_query):
        """Validate if file content matches search criteria"""
        if not content or not validation_query:
            return True
        
        # Simple validation: check if the search terms appear in the content
        search_terms = validation_query.lower().split()
        content_lower = content.lower()
        
        # Check for exact phrase match first
        if validation_query.lower() in content_lower:
            return True
            
        # Fall back to checking if all search terms are present
        return all(term in content_lower for term in search_terms)
    
    def download_file(self, repo, path, destination_folder, validation_query=None):
        """Download a file from GitHub to local destination if it passes validation"""
        content = self.get_file_content(repo, path)
        if not content:
            return False
            
        # Validate content against search query
        if validation_query and not self.validate_file_content(content, validation_query):
            print(f"File {repo}/{path} did not pass validation. Skipping.")
            return False
            
        # Create destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)
        
        # Create repository folder structure
        repo_folder = repo.replace('/', '_')
        full_destination = os.path.join(destination_folder, repo_folder)
        os.makedirs(full_destination, exist_ok=True)
        
        # Create folder for file path (preserve directory structure)
        file_dir = os.path.dirname(path)
        if file_dir:
            path_dir = os.path.join(full_destination, file_dir)
            os.makedirs(path_dir, exist_ok=True)
            file_path = os.path.join(path_dir, os.path.basename(path))
        else:
            file_path = os.path.join(full_destination, os.path.basename(path))
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        
        # Double check after writing (in case of encoding issues)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                saved_content = f.read()
            
            if validation_query and not self.validate_file_content(saved_content, validation_query):
                print(f"File {repo}/{path} failed post-save validation. Removing.")
                os.remove(file_path)
                
                # Check if directory is empty and remove if it is
                if file_dir:
                    parent_dir = os.path.dirname(file_path)
                    if parent_dir and os.path.exists(parent_dir) and not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                
                # Check if repo folder is empty and remove if it is
                if os.path.exists(full_destination) and not os.listdir(full_destination):
                    os.rmdir(full_destination)
                    
                return False
        except Exception as e:
            print(f"Error during post-save validation: {e}")
        
        return True

    def download_files_parallel(self, items, destination_folder, validation_query=None, max_workers=5):
        """Download multiple files in parallel"""
        successful = 0
        failed = 0
        
        def download_worker(item):
            repo = item['repository']['full_name']
            path = item['path']
            print(f"Downloading {repo}/{path}...")
            
            if self.download_file(repo, path, destination_folder, validation_query):
                print(f"Successfully downloaded {repo}/{path}")
                return True
            else:
                print(f"Failed to download {repo}/{path}")
                return False
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(download_worker, items))
            
        successful = sum(results)
        failed = len(results) - successful
        
        return successful, failed

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='GitHub Code Downloader')
    parser.add_argument('-q', '--query', help='Search query')
    parser.add_argument('-l', '--language', help='Filter by language')
    parser.add_argument('-n', '--limit', type=int, default=30, help='Maximum number of results')
    parser.add_argument('-d', '--destination', default='github_downloads', help='Destination folder')
    parser.add_argument('-p', '--parallel', type=int, default=5, help='Number of parallel downloads')
    parser.add_argument('-a', '--all', action='store_true', help='Download all results without prompting')
    return parser.parse_args()

def interactive_mode(downloader):
    """Run the downloader in interactive mode"""
    print("GitHub Code Downloader (Interactive Mode)")
    print("========================================")
    
    while True:
        print("\n1. Search and download code")
        print("2. Exit")
        choice = input("\nChoose an option: ")
        
        if choice == '2':
            break
            
        if choice == '1':
            query = input("Enter search query: ")
            language = input("Filter by language (optional, press Enter to skip): ")
            max_results = input("Maximum number of results (default: 30): ")
            
            try:
                max_results = int(max_results) if max_results else 30
            except ValueError:
                max_results = 30
                
            if not language:
                language = None
                
            print(f"Searching for '{query}'...")
            results = downloader.search_code(query, language, max_results)
            
            if not results:
                print("No results found.")
                continue
                
            print(f"Found {len(results)} matching files.")
            
            for i, item in enumerate(results):
                repo = item['repository']['full_name']
                path = item['path']
                print(f"{i+1}. {repo}/{path}")
            
            selection = input("\nEnter numbers to download (comma-separated) or 'all': ")
            
            download_dir = "github_downloads"
            validation_option = input("Validate downloaded files against search query? (y/n, default: y): ")
            validation_query = query if validation_option.lower() != 'n' else None
            
            if validation_query:
                print("Files that don't contain the search phrase will be automatically removed.")
            
            selected_items = []
            if selection.lower() == 'all':
                selected_items = results
            else:
                try:
                    indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                    selected_items = [results[idx] for idx in indices if 0 <= idx < len(results)]
                except ValueError:
                    print("Invalid selection.")
                    continue
            
            if not selected_items:
                print("No valid items selected.")
                continue
            
            print(f"Downloading {len(selected_items)} files...")
            successful, failed = downloader.download_files_parallel(selected_items, download_dir, validation_query)
            print(f"Download complete: {successful} successful, {failed} failed.")
        else:
            print("Invalid option.")

def main():
    # Hardcoded GitHub token (replace this with your actual token)
    token = "YOUR_GITHUB_TOKEN_HERE"
    
    # Check for GitHub token in environment variable if not hardcoded
    if token == "YOUR_GITHUB_TOKEN_HERE":
        token = os.environ.get('GITHUB_TOKEN')
        print("Warning: Using placeholder token. For better results, edit the code to add your token.")
    
    if not token or token == "YOUR_GITHUB_TOKEN_HERE":
        print("Warning: No GitHub token found. API rate limits will be restricted.")
        print("Either set GITHUB_TOKEN environment variable or edit the code to add your token.")
    
    downloader = GitHubCodeDownloader(token)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # If query is provided, run in command line mode
    if args.query:
        print(f"Searching for '{args.query}'...")
        results = downloader.search_code(args.query, args.language, args.limit)
        
        if not results:
            print("No results found.")
            return
            
        print(f"Found {len(results)} matching files.")
        
        # Display results if not downloading all
        if not args.all:
            for i, item in enumerate(results):
                repo = item['repository']['full_name']
                path = item['path']
                print(f"{i+1}. {repo}/{path}")
            
            selection = input("\nEnter numbers to download (comma-separated) or 'all': ")
            
            selected_items = []
            if selection.lower() == 'all':
                selected_items = results
            else:
                try:
                    indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                    selected_items = [results[idx] for idx in indices if 0 <= idx < len(results)]
                except ValueError:
                    print("Invalid selection.")
                    return
        else:
            selected_items = results
            
        validation_query = args.query
        
        print(f"Downloading {len(selected_items)} files...")
        print("Files that don't contain the search phrase will be automatically removed.")
        successful, failed = downloader.download_files_parallel(
            selected_items, 
            args.destination, 
            validation_query,
            args.parallel
        )
        print(f"Download complete: {successful} successful, {failed} failed.")
    else:
        # If no query, run in interactive mode
        interactive_mode(downloader)

if __name__ == "__main__":
    main()