import requests
import requests
from nbformat import read
from github import Github
from typing import Tuple, List, Optional, Dict
import tokenize
import io


class Repo:
    """
    This Repo class fetches the repositories and prepares them for
    analysis on GPT by implementing memory management techniques
    for large repositories and the files within them
    """
    url: str
    #Tuple of unwanted directories
    unwanted: Tuple = (
    "doc", "test", ".github", ".gitignore", "LICENSE",
    "CONTRIBUTING", ".gitattributes", "CHANGELOG", ".idea"
    )
    file_extensions = (
    ".py",
    ".ipynb"
    ".js",
    ".java",
    ".c",
    ".cpp",
    ".cc",
    ".cxx",
    ".cs",
    ".rb",
    ".swift",
    ".go",
    ".rs",
    ".kt",
    ".kts",
    ".php",
    ".ts",
    ".html",
    ".htm",
    ".css",
    ".sql",
    ".r",
    ".m",
    ".pl",
    ".sh",
    ".ps1",
    ".lua",
    ".m",
    ".groovy",
    ".scala",
    ".dart",
    ".jl",
    ".hs",
    ".vb",
    ".swift"
    )
    g = Github()
    # Maximum number of tokens allowed
    MAX_TOKENS: Optional[int] = 500


    def __init__(self, url: str):
        self.url = url 


    def _get_repo_urls(self):
        """
        This function returns list of the file urls in a single repository,
        it also performs cleaning to select only the important files which
        affect the GPT's decision making
        """ 
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        # Split the URL by '/'
        parts = self.url.split('/')
        # Extract the last part (username)
        username = parts[-1]
        user = self.g.get_user(username) 
        repos = user.get_repos()
        repo_urls = []
        file_urls = []
        repo_dict = {}
        for repo in repos:
            if len(file_urls) != 0:
                repo_urls.append(file_urls)
                repo_dict[len(repo_urls)-1] = repo_url
            repo_url = ""
            file_urls = []
            contents = repo.get_contents("")
            while (len(contents)) > 0:
                file_content = contents.pop(0)
                if file_content.path.startswith(self.unwanted) == True:
                    continue
                elif file_content.type != "dir" and file_content.path.endswith(self.file_extensions) == False:
                    continue
                else:
                    if file_content.type == "dir":
                        contents.extend(repo.get_contents(file_content.path))
                    else:
                        file_urls.append(file_content.raw_data["download_url"])
            repo_url = repo.url.replace("api.", "")
            repo_url = repo_url.replace("repos/", "")
        return repo_urls, repo_dict


    def _preprocess_repository_code(self, file_urls: List[str]) -> List[str]:
        """
        This function performs preprocessing on each file
        in the repository which includes memory management techniques
        to avoid exceeding GPT maximum token limit
        """
        preprocessed_code = []
        for file_url in file_urls:
            code = ""

            if file_url.endswith('.ipynb'):
                # Preprocessing Jupyter notebook file
                notebook = read(file_url, as_version=4)
                for cell in notebook['cells']:
                    if cell['cell_type'] == 'code':
                        code += cell['source'] + "\n"
            else:
                # Preprocessing code files
                response = requests.get(file_url)
                if response.status_code == 200:
                    code = response.text

            # Tokenizing the code and handling token limits
            tokens = list(tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline))
            if len(tokens) > self.MAX_TOKENS:
                tokens = tokens[:self.MAX_TOKENS]
                code = tokenize.untokenize(tokens).decode('utf-8')

            preprocessed_code.append(code)

        return preprocessed_code

    
    def __call__(self):
        """
        Execute Repo class
        """
        preprocessed_code = []
        repo_urls, repo_dict = self._get_repo_urls()
        for file_urls in repo_urls:
            preprocessed_code.append(self._preprocess_repository_code(file_urls=file_urls))
        return preprocessed_code, repo_dict


