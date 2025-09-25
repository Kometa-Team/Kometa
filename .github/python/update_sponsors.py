import os, requests
from datetime import datetime

pat = os.getenv("GITHUB_PAT")

class Sponsor:
    def __init__(self, json_data):
        self.name = json_data["sponsorEntity"]["login"]
        self.url = json_data["sponsorEntity"]["url"]
        self.web_url = json_data["sponsorEntity"]["websiteUrl"]
        self.created_at = datetime.strptime(json_data["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.public = json_data["privacyLevel"] == "PUBLIC"
        self.one_time = json_data["tier"]["isOneTime"]
        self.amount = json_data["tier"]["monthlyPriceInCents"]

    def small_logo(self):
        return self.logo(50)

    def large_logo(self):
        return self.logo(80)

    def logo(self, size):
        return f'<a href="{self.url}"><img src="{self.url}.png" width="{size}px" alt="User avatar: {self.name}" /></a>'

    def __str__(self):
        return f"{self.name:<20} ({self.created_at}) Public: {self.public:<5} One-Time: {self.one_time:<5} Amount ${int(self.amount/100)}"

def get_sponsors():
    sponsors_list = []
    cursor = None
    while True:
        cursor_text = f', after: "{cursor}"' if cursor is not None else ''
        query = f'''
        query {{
            viewer {{
                login
                sponsorshipsAsMaintainer(first: 100, orderBy: {{field: CREATED_AT, direction: DESC}}, includePrivate: false, activeOnly: true{cursor_text}) {{
                    totalCount
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    nodes {{
                        sponsorEntity {{
                            ... on Organization {{
                                name
                                login
                                url
                                websiteUrl
                            }}
                            ... on User {{
                                name
                                login
                                url
                                websiteUrl
                            }}
                        }}
                        createdAt
                        privacyLevel
                        tier {{
                            isOneTime
                            monthlyPriceInCents
                        }}
                    }}
                }}
            }}
        }}'''
        response = requests.request("POST", "https://api.github.com/graphql", headers={"Authorization": f"Bearer {pat}"}, json={"query": query})
        response_json = response.json()["data"]["viewer"]["sponsorshipsAsMaintainer"]
        cursor = response_json["pageInfo"]["endCursor"]
        sponsors_list.extend([Sponsor(s) for s in response_json["nodes"]])
        if response_json["pageInfo"]["hasNextPage"] is False:
            break
    sponsors_list.sort(key=lambda x: x.created_at, reverse=True)
    return sponsors_list

premium = []
standard = []
for sponsor in get_sponsors():
    if sponsor.amount < 2500:
        standard.append(sponsor.small_logo())
    else:
        premium.append(sponsor.large_logo())


with open("README.md", "r") as f:
    readme_data = f.readlines()

for i, line in enumerate(readme_data):
    if line.startswith("<!--premium-sponsors-->"):
        readme_data[i] = f"<!--premium-sponsors-->{'&nbsp;&nbsp;'.join(premium)}\n"
    if line.startswith("<!--standard-sponsors-->"):
        readme_data[i] = f"<!--standard-sponsors-->{'&nbsp;&nbsp;'.join(standard)}\n"

with open("README.md", "w") as f:
    f.writelines(readme_data)

