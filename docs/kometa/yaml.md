# YAML Files Explained

All of Kometa's Config, Metadata, Overlay, and Playlist Files are written in the YAML data structure.

This tutorial will help you understand the specific parts of the files.

## Example YAML File

```yaml
libraries:
  Movies:
    collection_files:
      - default: basic
      - default: imdb
    overlay_files:
      - default: ribbon
        template_variables:
          use_metacritic: false
          use_common: false
  TV Shows:
    collection_files:
      - default: basic
      - default: imdb
    overlay_files:
      - default: ribbon
settings:
  cache: true
  cache_expiration: 60
  asset_directory:
    - config/movie assets
    - config/tv assets
```

## Basic YAML Syntax

A YAML format primarily uses 3 node types:

1. Dictionaries/Mappings:
    The content of a mapping node is an unordered set of key/value node pairs, with the restriction that each of the keys is unique. YAML places no further restrictions on the nodes. 

2. Lists/Arrays:
    The content of a list node is an ordered series of zero or more nodes. In particular, a sequence may contain the same node more than once. It could even contain itself. 

3. Literals (Strings, numbers, boolean, etc.):
    The content of a scalar node is an opaque datum that can be presented as a series of zero or more Unicode characters.

Let us try and identify where these appear in the sample YAML file we saw earlier.

```yaml
# Starts with a top level Dictionary with keys `libraries` and `settings`
libraries:                        # Value is a Dictionary with keys `Movies` and `TV Shows`
  Movies:                         # Value is a Dictionary with keys `collection_files` and `overlay_files`
    collection_files:             # Value is a List with two Items
      - default: basic                # List Item is a Dictionary with one key pair whose value is a String Literal
      - default: imdb                 # List Item is a Dictionary with one key pair whose value is a String Literal
    overlay_files:                # Value is a List with one Item
      - default: ribbon               # List Item is a Dictionary with keys `default` and `template_variables` with `default`'s value a String Literal
        template_variables:       # Value is a Dictionary with keys `use_metacritic` and `use_common`
          use_metacritic: false   # Value is a Boolean Literal
          use_common: false       # Value is a Boolean Literal
  TV Shows:                       # Value is a Dictionary with keys `collection_files` and `overlay_files`
    collection_files:             # Value is a List with two Items
      - default: basic                # List Item is a Dictionary with one key pair whose value is a String Literal
      - default: imdb                 # List Item is a Dictionary with one key pair whose value is a String Literal
    overlay_files:                # Value is a List with one Item
      - default: ribbon               # List Item is a Dictionary with one key pair whose value is a String Literal
settings:                         # Value is a Dictionary with keys `cache` and `cache_expiration`
  cache: true                     # Value is a Boolean Literal
  cache_expiration: 60            # Value is a Number Literal
  asset_directory:                # Value is a List with two Items
    - config/movie assets         # List Item is a String Literal
    - config/tv assets            # List Item is a String Literal
```

## Indentation 

A YAML file relies on whitespace and indentation to indicate nesting. The number of spaces used for indentation doesn’t matter as long as they are consistent.

**It is critical to note that tab characters cannot be used for indentation in YAML files; only spaces can be used.**

```yaml
libraries:                        # Nesting Level 1
  Movies:                         # Nesting Level 2
    collection_files:             # Nesting Level 3
      - default: basic                # Nesting Level 4
      - default: imdb                 # Nesting Level 4
    overlay_files:                # Nesting Level 3
      - default: ribbon               # Nesting Level 4
        template_variables:       # Nesting Level 5
          use_metacritic: false   # Nesting Level 6
          use_common: false       # Nesting Level 6
  TV Shows:                       # Nesting Level 2
    collection_files:             # Nesting Level 3
      - default: basic                # Nesting Level 4
      - default: imdb                 # Nesting Level 4
    overlay_files:                # Nesting Level 3
      - default: ribbon               # Nesting Level 4
settings:                         # Nesting Level 1
  cache: true                     # Nesting Level 2
  cache_expiration: 60            # Nesting Level 2
```

## Dictionaries

Dictionaries are used to associate key/value pairs that are unordered. Dictionaries can be nested by increasing the indentation, or new dictionaries can be created at the same level by resolving the previous one.

```yaml
cache: true
cache_expiration: 60
```

The "keys" are `cache` and `cache_expiration` and the "values" are `true` and `60` respectively.

### In-Line Dictionaries

you can represent a dictionary on a single line by using `{` and `}`

```yaml
settings: {cache: true, cache_expiration: 60}
```

is equivalent to

```yaml
settings:
  cache: true
  cache_expiration: 60
```

## Lists

Lists in YAML are represented by using the hyphen (-) and space. They are ordered and can be embedded inside a map using indentation.

```yaml
asset_directory:
  - config/movie assets
  - config/tv assets
```

The first item in the list is `config/movie assets` and the second is `config/tv assets`.

### In-Line Lists

you can represent a dictionary on a single line by using `[` and `]`

```yaml
settings:
    asset_directory: [config/movie assets, config/tv assets]
```

is equivalent to

```yaml
settings:
    asset_directory:
      - config/movie assets
      - config/tv assets
```

## Literals

Literals can come in multiple types:

* String: any sequence of characters

* Number: any representation of a number

* Boolean: `true` or `false`

### String Literals

The string literals do not require to be quoted. It is only important to quote them when they contain a value that can be mistaken as a special character.

Here is an example where the string has to be quoted as `&` and `:` are special characters.

YAML Special Characters: `{`, `}`, `[`, `]`, `,`, `&`, `:`, `*`, `#`, `?`, `|`, `-`, `<`. `>`, `=`, `!`, `%`, `@`, `\`

There are many occurrences of these special characters where quotes are not needed but if the YAML fails to load it could easily be because one of these are unquoted.

```yaml
message1: YAML & JSON                 # breaks as a & is a special character
message2: "YAML & JSON"               # Works as the string is quoted
message: 3: YAML                      # breaks as a : is a special character
"message: 3": YAML                    # Works as the key string is quoted
```

#### Multiline Strings 

Strings can be interpreted as multiline using the pipe (`|`) character.

```yaml
message: |
 this is
 a real multiline
 message
```

This would be read as `this is\na real multiline\nmessage`

## Comments

YAML file also supports comments, unlike JSON. A comment starts with #.

```yaml
# Strats with a top level Dictionary with keys `libraries` and `settings`
libraries:                        # Value is a Dictionary with keys `Movies` and `TV Shows`
```

Everything after `#` on a line is ignored.

## Anchors and Aliases

With a lot of configuration, configuration files can become quite large.

In YAML files, anchors (`&`) and aliases (`*`) are used to avoid duplication. When writing large configurations in YAML, it is common for a specific configuration to be repeated. For example, the vars config is repeated for all three services in the following YAML snippet.

```yaml
libraries:
  Movies:
    collection_files:
      - default: basic
      - default: imdb
    overlay_files:
      - default: ribbon
        template_variables:
          use_metacritic: false
          use_common: false
  TV Shows:
    collection_files:
      - default: basic
      - default: imdb
    overlay_files:
      - default: ribbon
```

As more and more things are repeated for large configuration files, this becomes tedious.

Anchors and aliases allow us to rewrite the same snippet without having to repeat any configuration.

Anchors (`&`) are used to define a chunk of configuration, and aliases (`*`) are used to refer to that chunk at a different part of the configuration.

```yaml
libraries:
  Movies:
    collection_files: &paths   # Anchor called `paths`
      - default: basic
      - default: imdb
    overlay_files:
      - default: ribbon
        template_variables:
          use_metacritic: false
          use_common: false
  TV Shows:
    collection_files: *paths   # Alias to call the above `paths` section
    overlay_files:
      - default: ribbon
```