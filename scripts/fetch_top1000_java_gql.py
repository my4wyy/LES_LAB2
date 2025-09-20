import os
import csv
import requests
import time

GITHUB_API = "https://api.github.com/graphql"
TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("set the env var GITHUB_TOKEN before running")

headers = {
    "Authorization": f"bearer {TOKEN}",
    "Accept": "application/vnd.github.v4+json"
}

query = """
query ($queryString: String!, $first: Int!, $after: String) {
  search(query: $queryString, type: REPOSITORY, first: $first, after: $after) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        nameWithOwner
        url
        description
        stargazerCount
        createdAt
        pushedAt
        diskUsage
        forkCount
    releases { totalCount }
        primaryLanguage { name }
      }
    }
  }
}
"""

def run_query(variables):
    r = requests.post(GITHUB_API, json={'query': query, 'variables': variables}, headers=headers)
    if r.status_code != 200:
        raise Exception(f"query failed status {r.status_code} body {r.text}")
    return r.json()

def main():
    query_string = "language:Java sort:stars-desc"
    per_page = 100
    after = None
    collected = []
    total_to_collect = 1000
    while len(collected) < total_to_collect:
        variables = {"queryString": query_string, "first": per_page, "after": after}
        data = run_query(variables)
        repos = data["data"]["search"]["nodes"]
        for repo in repos:
            collected.append({
                "nameWithOwner": repo.get("nameWithOwner"),
                "url": repo.get("url"),
                "description": repo.get("description") or "",
                "stargazerCount": repo.get("stargazerCount"),
                "createdAt": repo.get("createdAt"),
                "pushedAt": repo.get("pushedAt"),
                "diskUsage": repo.get("diskUsage"),
                "forkCount": repo.get("forkCount"),
                "releaseCount": (repo.get("releases") or {}).get("totalCount"),
                "primaryLanguage": repo.get("primaryLanguage", {}).get("name")
            })
            if len(collected) >= total_to_collect:
                break
        page_info = data["data"]["search"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        after = page_info["endCursor"]
        time.sleep(1)
    keys = ["nameWithOwner","url","description","stargazerCount","createdAt","pushedAt","diskUsage","forkCount","releaseCount","primaryLanguage"]
    os.makedirs("data", exist_ok=True)
    with open("data/top1000_java_repos.csv","w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in collected:
            writer.writerow(row)
    print(f"saved {len(collected)} repos to data/top1000_java_repos.csv")

if __name__ == "__main__":
    main()
