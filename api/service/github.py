import os
import requests
from datetime import datetime
from typing import Dict, Any

MetricsDTO = Dict[str, Any]

def get_basic_metrics(user: str) -> MetricsDTO:
    url = 'https://api.github.com/graphql'
    header = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN', '')}"}

    if not header["Authorization"]:
        print("❌ ERRO: GITHUB_TOKEN não encontrado!")
        return {}

    print(f"📡 Buscando métricas de {user}...")

    def query_for_year(user: str, from_date: str, to_date: str) -> str:
        return f"""
        query {{
            user(login: "{user}") {{
                contributionsCollection(from: "{from_date}", to: "{to_date}") {{
                    totalCommitContributions,
                    totalIssueContributions,
                    totalPullRequestContributions,
                    totalPullRequestReviewContributions
                }}
                followers {{
                    totalCount
                }}
                repositories(isFork: false, first: 100) {{
                    nodes {{
                        name,
                        stargazerCount,
                        forkCount
                    }}
                }}
            }}
        }}
        """

    metrics: MetricsDTO = {
        "all_repos": 0,
        "all_stars": 0,
        "all_forks": 0,
        "all_commits": 0,
        "all_issues": 0,
        "all_prs": 0,
        "all_prs_review": 0,
        "all_followers": 0
    }

    current_year = datetime.now().year
    start_year = 2008

    for year in range(start_year, current_year + 1):
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"

        query = query_for_year(user, from_date, to_date)

        try:
            res = requests.post(url, json={'query': query}, headers=header)
            res.raise_for_status()
            data = res.json()
            contributions = data["data"]["user"]["contributionsCollection"]
            
            metrics["all_commits"] += contributions["totalCommitContributions"]
            metrics["all_issues"] += contributions["totalIssueContributions"]
            metrics["all_prs"] += contributions["totalPullRequestContributions"]
            metrics["all_prs_review"] += contributions["totalPullRequestReviewContributions"]

            if year == start_year:
                metrics["all_followers"] = data["data"]["user"]["followers"]["totalCount"]
                for repos in data["data"]["user"]["repositories"]["nodes"]:
                    metrics["all_repos"] += 1
                    metrics["all_stars"] += repos["stargazerCount"]
                    metrics["all_forks"] += repos["forkCount"]

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar dados do GitHub: {e}")
            return {}

    return metrics
