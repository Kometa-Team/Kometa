# Github Attributes

Configuring [Github](https://github.com/) is optional but can allow you to avoid rate limits when requesting data from github.

Requests made with a github token have a higher rate limit than anonymous requests.

A `github` mapping is in the root of the config file.

Below is a `github` mapping example and the full set of attributes:
```yaml
github:
  token: ################################
```

| Attribute          | Allowed Values                                                             | Default | Required |
|:-------------------|:---------------------------------------------------------------------------|:--------|:--------:|
| `token`            | Github Personal Access Token                                               | N/A     | &#9989;  |

* The Github Personal Access Token can be generated [here](https://github.com/settings/tokens).
