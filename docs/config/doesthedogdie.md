# DoesTheDogDie Attributes

Configuring [DoesTheDogDie](https://doesthedogdie.com/) is optional but is required for MyAnimeList based operations to function.

A `doesthedogdie` mapping is in the root of the config file.

Below is a `doesthedogdie` mapping example and the full set of attributes:

```yaml
doesthedogdie:
  apikey: ################################
```

| Attribute       | Allowed Values                        |                  Required                  |
|:----------------|:--------------------------------------|:------------------------------------------:|
| `apikey`        | DoesTheDogDie API Key                 | :fontawesome-solid-circle-check:{ .green } |

All other attributes will be filled in by Plex Meta Manager.

To connect to DoesTheDogDie.com you must create an account and retrieve your API Key:

1. [Create an account](https://www.doesthedogdie.com/signup) or [Log-in to your existing account](https://www.doesthedogdie.com/login)
2. Navigate to [Your Profile](https://www.doesthedogdie.com/profile)
3. Select REVEAL next to API Key to obtain your API Key