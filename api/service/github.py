import os
import requests
from datetime import datetime
from typing import Dict, Any

MetricsDTO = Dict[str, Any]

def get_basic_metrics(user: str) -> MetricsDTO:
    url = 'https://api.github.com/graphql'
    header = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}

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

    def add_metrics(metrics: MetricsDTO, data: MetricsDTO) -> None:
        metrics["all_commits"] += data["totalCommitContributions"]
        metrics["all_issues"] += data["totalIssueContributions"]
        metrics["all_prs"] += data["totalPullRequestContributions"]
        metrics["all_prs_review"] += data["totalPullRequestReviewContributions"]

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
        res = requests.post(url, json={'query': query}, headers=header)
        res.raise_for_status()
        data = res.json()

        contributions = data["data"]["user"]["contributionsCollection"]
        add_metrics(metrics, contributions)

        if year == start_year:
            metrics["all_followers"] = data["data"]["user"]["followers"]["totalCount"]
            for repos in data["data"]["user"]["repositories"]["nodes"]:
                metrics["all_repos"] += 1
                metrics["all_stars"] += repos["stargazerCount"]
                metrics["all_forks"] += repos["forkCount"]

    return metrics
