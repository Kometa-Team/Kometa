# Dynamic Collections

Plex Meta Manager can dynamically create collections based on different criteria, such as
* Collections based on the Collections from TMDb for every item in the library. ([Star Wars](https://www.themoviedb.org/collection/10-star-wars-collection), [Harry Potter](https://www.themoviedb.org/collection/1241), etc...)
* Collections based on each of a Users Trakt Lists
* Collections for the top `X` popular people on TMDb (Bruce Willis, Tom Hanks, etc...)
* Collections for each decade represented in the library (Best of 1990s, Best of 2000s, etc...)
* Collections for each of the moods/styles within a Music library (A Cappella, Pop Rock, etc...)

The main purpose of dynamic collections is to automate the creation of collections which would otherwise require considerable user input and repetition (such as creating a collection for every genre).

Each dynamic collection must have a mapping name (just like standard collections), which is also attached to the collection as a label to mark it as having been created by this dynamic collection.

This example will create a collection for every TMDb Collection associated with items in the library.

```yaml
dynamic_collections:
  TMDb Collections:          # This name is the mapping name
    type: tmdb_collection
    remove_suffix: "Collection"
```

## Collection Naming

By default, the collections generated will be named for the thing being used to create them; things like genres, countries, actors or even Trakt List Names.

There are many attributes that can change the titles, including `title_format`, `remove_suffix`, `remove_prefix`, `key_name_override`, and `title_override` all detailed below.

## Dynamic Keys & Key Names

A `dynamic key` or `key` for short is used to refer to a specific value/result from the dynamic collection criteria that will be used to create the collection.

A `key_name` is the name that replaces `<<key_name>>` in `title_format` to create the collection titles for each key.

An example of some keys and their names that would be generated from a `tmdb_collection` dynamic collection are
* `key`: "10"
  * `key_name`: Star Wars Collection
* `key`: "1241"
  * `key_name`: Harry Potter Collection

### Example Key Usage

Keys can be used for a number of purposes, examples can be found throughout this page. A few examples are shown below:

* Excluding the "Horror" key from the `Genre` dynamic collection definition

```yaml
dynamic_collections:
  Genres:         # mapping name does not matter, just needs to be unique
    type: genre
    exclude:
      - Horror
```

* Using the `key_name_override` attribute to change the formatting of "France" to "French" so that a collection can be named "French Cinema" instead of simply "France"
  * This particular example also uses the `title_format` attribute to manipulate the naming convention of the collections.

```yaml
dynamic_collections:
  Countries:         # mapping name does not matter, just needs to be unique
    type: country
    title_format: <<key_name>> Cinema
    key_name_override:
      France: French
```

* Using the `addons` attribute to combine multiple `keys`, i.e. merging "MTV2", "MTV3" and "MTV (UK)" into one "MTV" collection.
  * When doing this, individual collections will not be created for the individual MTV collections, instead they will be merged within the "MTV" collection.

```yaml
dynamic_collections:
  networks:
    type: network
    addons:
      MTV:
        - MTV2
        - MTV3
        - MTV (UK)
```

## Attributes

| Attribute                                   | Description                                                                                                                    |                  Required                  |
|:--------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|
| [`type`](#type--data)                       | Type of Dynamic Collection to be created.                                                                                      | :fontawesome-solid-circle-check:{ .green } |
| [`data`](#type--data)                       | Data to determine how dynamic collections with a certain `type` are created.                                                   |             Depends on `type`              |
| [`exclude`](#exclude)                       | Exclude this list of keys from being created into collections.                                                                 |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`addons`](#addons)                         | Defines how multiple keys can be combined under a parent key.                                                                  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`template`](#template)                     | Name of the template to use for these dynamic collections.                                                                     |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`template_variables`](#template-variables) | Defines how template variables can be defined by key.                                                                          |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`other_template`](#other-template)         | Name of the template to use for the other collection.                                                                          |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`remove_suffix`](#remove-prefixsuffix)     | Removes the defined suffixes from the key before it's used in the collection title.                                            |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`remove_prefix`](#remove-prefixsuffix)     | Removes the defined prefixes from the key before it's used in the collection title.                                            |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`title_format`](#title-format)             | This is the format for the collection titles.                                                                                  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`key_name_override`](#key-name-override)   | Defines how key names can be overridden before they are formatted into collection titles.                                      |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`title_override`](#title-override)         | Defines how collection titles can be overridden ignoring title formatting.                                                     |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`custom_keys`](#custom-keys)               | Defines if custom keys are allowed.                                                                                            |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`test`](#test)                             | Will add `test: true` to all collections for test runs.                                                                        |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`sync`](#sync)                             | Will remove dynamic collections that are no longer in the creation list.                                                       |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`include`](#include)                       | Define a list of keys to be made into collections.                                                                             |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`other_name`](#other-name)                 | Used in combination with `include`. When defined, all keys not in `include` or `addons` will be combined into this collection. |  :fontawesome-solid-circle-xmark:{ .red }  |

{%
   include-markdown "./dynamic_types.md"
%}