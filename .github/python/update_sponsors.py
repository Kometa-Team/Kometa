import os, requests
from datetime import datetime

pat = os.getenv("GITHUB_PAT")


class SponsorBase:
    def __init__(self):
        self.name = None
        self.url = None
        self.web_url = None
        self.amount = None

    def bronze_logo(self):
        return self.logo(50)

    def silver_logo(self):
        return self.logo(80)

    def gold_logo(self):
        return self.logo(120)

    def logo(self, size):
        return f'<a href="{self.url}"><img src="{self.url}.png" width="{size}px" alt="User avatar: {self.name}" /></a>'

    def __str__(self):
        return f"{self.name:<20} Amount ${self.amount/100:.2f}"


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


gold_sponsors = []
silver_sponsors = []
bronze_sponsors = []
standard_sponsors = []
private_sponsors = [s.name for s in get_sponsors(private=True) if s.public is False]
active_sponsors = {s.name: s for s in get_sponsors(active=True)}

for sponsor in get_lifetime():
    if sponsor.name in private_sponsors:
        continue
    #print(sponsor)
    active_amount = active_sponsors[sponsor.name].amount if sponsor.name in active_sponsors else 0
    if sponsor.amount >= 25000 or active_amount >= 2500:
        gold_sponsors.append(sponsor.gold_logo())
    elif sponsor.amount >= 10000 or active_amount >= 1000:
        silver_sponsors.append(sponsor.silver_logo())
    elif sponsor.amount >= 5000 or active_amount >= 500:
        bronze_sponsors.append(sponsor.bronze_logo())
    else:
        standard_sponsors.append(sponsor.bronze_logo())


#print(f"gold_sponsors: {len(gold_sponsors)}")
#print(f"silver_sponsors: {len(silver_sponsors)}")
#print(f"bronze_sponsors: {len(bronze_sponsors)}")
#print(f"standard_sponsors: {len(standard_sponsors)}")

with open("README.md", "r") as f:
    readme_data = f.readlines()

for i, line in enumerate(readme_data):
    if line.startswith("<!--gold-sponsors-->"):
        readme_data[i] = f"<!--gold-sponsors-->{'&nbsp;&nbsp;'.join(gold_sponsors)}\n"
    if line.startswith("<!--silver-sponsors-->"):
        readme_data[i] = f"<!--silver-sponsors-->{'&nbsp;&nbsp;'.join(silver_sponsors)}\n"
    if line.startswith("<!--bronze-sponsors-->"):
        readme_data[i] = f"<!--bronze-sponsors-->{'&nbsp;&nbsp;'.join(bronze_sponsors)}\n"

with open("README.md", "w") as f:
    f.writelines(readme_data)
