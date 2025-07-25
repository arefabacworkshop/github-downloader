# GitHub Code Downloader

A Python application that searches GitHub for code matching your query and downloads the relevant files.

## Features

### Basic Downloader (github_code_downloader.py)
- Search GitHub code using keywords
- Filter results by programming language
- View and select specific files to download
- Download files while preserving repository structure

### Advanced Downloader (advanced_github_downloader.py)
- All features from the basic downloader
- Command-line arguments for non-interactive use
- Content validation against search terms
- Parallel downloading of multiple files
- **Pagination support** to download more than 100 files
- Enhanced directory structure preservation

## Setup

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```

3. (Optional but recommended) Set up a GitHub Personal Access Token:
   - Create a token at https://github.com/settings/tokens
   - Set it as an environment variable:
     - Windows: `set GITHUB_TOKEN=your_token_here`
     - Unix/Mac: `export GITHUB_TOKEN=your_token_here`
   - Or directly edit the token variable in the code file

## Usage

### Basic Downloader
Run the interactive application:
```
python github_code_downloader.py
```

### Advanced Downloader
Run in interactive mode:
```
python advanced_github_downloader.py
```

Run with command-line arguments:
```
python advanced_github_downloader.py -q "search query" -l language -n number_of_results -a
```

#### Command Line Options
- `-q, --query`: Search query (e.g., "import tensorflow")
- `-l, --language`: Filter by language (e.g., "python", "javascript")
- `-n, --limit`: Maximum number of results to fetch (default: 30)
- `-d, --destination`: Destination folder (default: "github_downloads")
- `-p, --parallel`: Number of parallel downloads (default: 5)
- `-a, --all`: Download all results without prompting

#### Examples
Download 200 Python files that import qiskit:
```
python advanced_github_downloader.py -q "import qiskit" -l python -n 200 -a
```

## Notes

- Without a GitHub token, API rate limits are very restricted (60 requests/hour)
- With a token, the limit increases to 5000 requests/hour
- Large files or binary files may not download correctly
- The advanced downloader can fetch more than 100 results using pagination
- GitHub search results are capped at 1000 items by the API