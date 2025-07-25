# GitHub Code Downloader

A simple Python application that searches GitHub for code matching your query and downloads only the relevant files.

## Features

- Search GitHub code using keywords
- Filter results by programming language
- View and select specific files to download
- Download files while preserving repository structure

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

## Usage

Run the application:
```
python github_code_downloader.py
```

- Choose option 1 to search for code
- Enter your search query (e.g., "pagination component", "database connection")
- Optionally filter by programming language (e.g., "python", "javascript")
- Select which files to download (comma-separated numbers or "all")
- Files will be downloaded to a "github_downloads" folder in the current directory

## Notes

- Without a GitHub token, API rate limits are very restricted (60 requests/hour)
- With a token, the limit increases to 5000 requests/hour
- Large files or binary files may not download correctly