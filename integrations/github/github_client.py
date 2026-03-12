import httpx
import os

class GitHubClient:
    def _get_headers(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("ERRO: GITHUB_TOKEN não encontrado.")
        
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        headers = self._get_headers()
        headers["Accept"] = "application/vnd.github.v3.diff" 
        
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def create_commit_status(self, repo_full_name: str, head_sha: str, state: str, description: str):
        """state: 'pending', 'success', 'error', ou 'failure'"""
        url = f"https://api.github.com/repos/{repo_full_name}/statuses/{head_sha}"
        payload = {
            "state": state,
            "description": description[:140], # GitHub limita a 140 chars
            "context": "Codebase Brain / Architecture Intelligence"
        }
        response = httpx.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()

    def create_pr_comment(self, repo_full_name: str, pr_number: int, body: str):
        """Posta o relatório Markdown como comentário no PR"""
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        payload = {"body": body}
        response = httpx.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()