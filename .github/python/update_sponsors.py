import os, requests
from datetime import datetime

pat = os.getenv("GITHUB_PAT")


class SponsorBase:
    def __init__(self):
        self.name = None
        self.url = None
        self.web_url = None
        self.amount = None

    def standard_logo(self):
        return self.logo(40)

    def plus_logo(self):
        return self.logo(70)

    def premium_logo(self):
        return self.logo(100)

    def logo(self, size):
        return f'<a href="{self.url}"><img src="{self.url}.png" width="{size}px" alt="User avatar: {self.name}" /></a>'

    def __str__(self):
        return f"{self.name:<20} Amount ${int(self.amount/100)}"


class LifetimeSponsor(SponsorBase):
    def __init__(self, json_data):
        super().__init__()
        self.name = json_data["sponsor"]["login"]
        self.url = json_data["sponsor"]["url"]
        self.web_url = json_data["sponsor"]["websiteUrl"]
        self.amount = json_data["amountInCents"]


class Sponsor(SponsorBase):
    def __init__(self, json_data):
        super().__init__()
        self.name = json_data["sponsorEntity"]["login"]
        self.url = json_data["sponsorEntity"]["url"]
        self.web_url = json_data["sponsorEntity"]["websiteUrl"]
        self.created_at = datetime.strptime(json_data["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.public = json_data["privacyLevel"] == "PUBLIC"
        self.one_time = json_data["tier"]["isOneTime"]
        self.amount = json_data["tier"]["monthlyPriceInCents"]


def get_lifetime():
    sponsors_list = []
    cursor = None
    while True:
        cursor_text = f', after: "{cursor}"' if cursor is not None else ''
        query = f'''
        query {{
            viewer {{
                login
                lifetimeReceivedSponsorshipValues(first: 100, orderBy: {{field: LIFETIME_VALUE, direction: DESC}}{cursor_text}) {{
                    totalCount
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    nodes {{
                        amountInCents
                        formattedAmount 
                        sponsor {{
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
                    }}
                }}
            }}
        }}'''


        response = requests.request("POST", "https://api.github.com/graphql", headers={"Authorization": f"Bearer {pat}"}, json={"query": query})
        response_json = response.json()["data"]["viewer"]["lifetimeReceivedSponsorshipValues"]
        cursor = response_json["pageInfo"]["endCursor"]
        sponsors_list.extend([LifetimeSponsor(s) for s in response_json["nodes"]])
        if response_json["pageInfo"]["hasNextPage"] is False:
            break
    return sponsors_list


def get_sponsors(private=False, active=False):
    sponsors_list = []
    cursor = None
    while True:
        cursor_text = f', after: "{cursor}"' if cursor is not None else ''
        query = f'''
        query {{
            viewer {{
                login
                sponsorshipsAsMaintainer(first: 100, orderBy: {{field: CREATED_AT, direction: DESC}}, includePrivate: {str(private).lower()}, activeOnly: {str(active).lower()}{cursor_text}) {{
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
                        isActive
                        isOneTimePayment 
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
    return sponsors_list


premium_sponsors = []
plus_sponsors = []
standard_sponsors = []
private_sponsors = [s.name for s in get_sponsors(private=True) if s.name is False]
for sponsor in get_sponsors(active=True):
    if sponsor.amount >= 2500:
        premium_sponsors.append(sponsor.premium_logo())
    elif sponsor.amount >= 1000:
        plus_sponsors.append(sponsor.plus_logo())
    else:
        standard_sponsors.append(sponsor.standard_logo())
    private_sponsors.append(sponsor.name)


for sponsor in get_lifetime():
    if sponsor.name in private_sponsors:
        continue
    if sponsor.amount >= 25000:
        premium_sponsors.append(sponsor.premium_logo())
    elif sponsor.amount >= 10000:
        plus_sponsors.append(sponsor.plus_logo())
    else:
        standard_sponsors.append(sponsor.standard_logo())

with open("README.md", "r") as f:
    readme_data = f.readlines()

for i, line in enumerate(readme_data):
    if line.startswith("<!--premium-sponsors-->"):
        readme_data[i] = f"<!--premium-sponsors-->{'&nbsp;&nbsp;'.join(premium_sponsors)}\n"
    if line.startswith("<!--plus-sponsors-->"):
        readme_data[i] = f"<!--plus-sponsors-->{'&nbsp;&nbsp;'.join(plus_sponsors)}\n"
    if line.startswith("<!--standard-sponsors-->"):
        readme_data[i] = f"<!--standard-sponsors-->{'&nbsp;&nbsp;'.join(standard_sponsors)}\n"

with open("README.md", "w") as f:
    f.writelines(readme_data)
