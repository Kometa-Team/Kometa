# GitHub Attributes

Configuring [GitHub](https://github.com/) is optional but can allow you to avoid rate limits when requesting data from 
GitHub.

Requests made with a GitHub token have a higher rate limit than anonymous requests.

A `github` mapping is in the root of the config file, sampled below.

```yaml title="config.yml GitHub sample"
github:
  token: thisismytoken
```

| Attribute          | Allowed Values                                                             | Default |                  Required                  |
|:-------------------|:---------------------------------------------------------------------------|:--------|:------------------------------------------:|
| `token`            | GitHub Personal Access Token                                               | N/A     | :fontawesome-solid-circle-check:{ .green } |

* The GitHub Personal Access Token can be generated [here](https://github.com/settings/tokens).
