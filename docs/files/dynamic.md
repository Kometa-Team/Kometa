---
hide:
  - tags
tags:
  - addons
  - append_addons
  - append_data
  - append_exclude
  - append_include
  - custom_keys
  - data
  - exclude
  - include
  - key_name_override
  - other_name
  - other_template
  - remove_addons
  - remove_data
  - remove_exclude
  - remove_include
  - remove_prefix
  - remove_suffix
  - sync
  - template
  - template_variables
  - test
  - title_format
  - title_override
  - tmdb_person
  - type
---

# Dynamic Collections

Kometa can dynamically create collections based on different criteria, such as

* Collections based on the Collections from TMDb for every item in the library. (
[Star Wars](https://www.themoviedb.org/collection/10-star-wars-collection), 
[Harry Potter](https://www.themoviedb.org/collection/1241), etc...)

* Collections based on each of a Users Trakt Lists

* Collections for the top `X` popular people on TMDb (Bruce Willis, Tom Hanks, etc...)

* Collections for each decade represented in the library (Best of 1990s, Best of 2000s, etc...)

* Collections for each of the moods/styles within a Music library (A Cappella, Pop Rock, etc...)

The main purpose of dynamic collections is to automate the creation of collections which would otherwise require 
considerable user input and repetition (such as creating a collection for every genre).

## Using Dynamic Collections

Each dynamic collection definition creates a set of collection definitions based on some given criteria and uses either 
the built-in default template or a user defined custom template to dynamically create collection definitions.

#### Collection Naming

By default, the collections generated will be named for the thing being used to create them; things like genres, 
countries, actors, or even Trakt List Names.

To change the name of the collection, you can use dynamic collection attributes including `title_format`, 
`remove_suffix`, `remove_prefix`, `key_name_override`, and `title_override` all detailed below.

#### Dynamic Keys & Key Names

A `dynamic key` or `key` for short is used to refer to a specific value/result from the dynamic collection criteria that
will be used to create the collection.

A `key_name` is the name that replaces `<<key_name>>` in `title_format` to create the collection titles for each key.

An example of some keys and their names that would be generated from a `tmdb_collection` dynamic collection are:

* `key`: "10"

    * `key_name`: Star Wars Collection

* `key`: "1241"

    * `key_name`: Harry Potter Collection

| `key` | `key_name`              |
|:------|:------------------------|
| 10    | Star Wars Collection    |
| 1241  | Harry Potter Collection |


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

* Using the `key_name_override` attribute to change the formatting of "France" to "French" so that a collection can be 
named "French Cinema" instead of simply "France"

    * This particular example also uses the `title_format` attribute to manipulate the naming convention of the
    collections.

```yaml
dynamic_collections:
  Countries:         # mapping name does not matter, just needs to be unique
    type: country
    title_format: <<key_name>> Cinema
    key_name_override:
      France: French
```

* Using the `addons` attribute to combine multiple `keys`, i.e. merging "MTV2", "MTV3" and "MTV (UK)" into one "MTV" 
collection.

    * When doing this, individual collections will not be created for the individual MTV collections, instead they will
    be merged within the "MTV" collection.

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

## Dynamic Collection Definition

Each dynamic collection definition must have a mapping name (just like standard collections) under the 
`dynamic_collections` attribute, which is also attached to the collection as a label to mark it as having been created 
by this dynamic collection.

??? example "Dynamic Collection Example (click to expand)"

    This example will create a collection for every TMDb Collection associated with items in the library.
    
    ```yaml
    dynamic_collections:
      TMDb Collections:          # This name is the mapping name
        type: tmdb_collection
        remove_suffix: "Collection"
    ```

### Attributes

??? blank "`type` & `data` - Used to specify the type of Dynamic Collection.<a class="headerlink" href="#type-data" title="Permanent link">¶</a>"

    <div id="type-data" />Used to specify the type of Dynamic Collection and its data. `type` is required for every 
    dynamic collection and `data` is required for any type that uses the attribute.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `type` & `data`
    
    **Accepted Values:** See [Dynamic Collection Types & Data](dynamic_types.md)

??? blank "`exclude` - Used to exclude a list of keys from being created into collections.<a class="headerlink" href="#exclude" title="Permanent link">¶</a>"

    <div id="exclude" />Used to exclude a list of `dynamic keys` from being created into collections.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `exclude`
    
    **Accepted Values:** List of keys

    ???+ example "Example"
        
        For example when making a `genre` dynamic collection definition you can exclude "Horror" from having a 
        collection created from the key.
        
        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter, just needs to be unique
            type: genre
            exclude:
              - Horror
        ```

??? blank "`addons` - Used to define how multiple keys can be combined under a parent key.<a class="headerlink" href="#addons" title="Permanent link">¶</a>"

    <div id="addons" />Used to define how multiple `dynamic keys` can be combined under a parent key.

    You can define custom parent keys under addons by just using the a key that doesnt exist; it will be considered a 
    custom key combining all keys into one key.

    <hr style="margin: 0px;">
    
    **Attribute:** `addons`
    
    **Accepted Values:** [Dictionary](../kometa/yaml.md#dictionaries) where the key is the `dynamic key` and the value is a
    list of `dynamic keys` to combine.

    ???+ example "Example"
        
        In this example the attribute is used to merge "MTV2", "MTV3" and "MTV (UK)" into the "MTV" collection.
        
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

??? blank "`template` - Used to define which templates are used.<a class="headerlink" href="#template" title="Permanent link">¶</a>"

    <div id="template" />Used to define which templates are used for these dynamic collections. Each dynamic collection 
    `type` has its own default template, but if you want to define and use your own template you can.

    Each template is passed a few template variables you can use.

    * `value`: The list of keys and addons

    * `key`: The dynamic key

    * `key_name`: The key after `key_name_override`, `remove_prefix`, or `remove_suffix` are run on it.

    <hr style="margin: 0px;">
    
    **Attribute:** `template`
    
    **Accepted Values:** Name of template or list of templates to use 

    ???+ example "Example"

        In this example the template removes the limit on the `smart_filter` so it shows all items in each network.

        Press the :fontawesome-solid-circle-plus: icon to learn more
        
        ```yaml
        templates:
          network collection: #(1)!
            smart_filter:
              sort_by: critic_rating.desc
              all:
                network: <<value>>
        dynamic_collections:
          Networks: #(2)!
            type: network
            title_format: <<key_name>>
            template: network collection #(3)!
        ```
        
        1. This is the mapping name of the template.
        2. This is the mapping name of the Dynamic Collection Definition.
        3. This must match the mapping name of the template you want to use.

??? blank "`template_variables` - Used to define template variables by key.<a class="headerlink" href="#template-variables" title="Permanent link">¶</a>"

    <div id="template-variables" />Used to define template variables by key. This attribute will allow multiple template
    variables to be set per dynamic key. 

    ???+ tip

        You can set a default value for a variable by using `default` instead of the dynamic key. 

    <hr style="margin: 0px;">
    
    **Attribute:** `template_variables`
    
    **Accepted Values:** [Dictionary](../kometa/yaml.md#dictionaries) where the key is the template variable and the value 
    is another [Dictionary](../kometa/yaml.md#dictionaries) where the key is the `dynamic key` of the collection you want 
    change the template variable for and the value is the new value for the template variable.

    ???+ example "Example"

        For example, when using `type: tmdb_collection` and you want to define a poster url for some collections.
        
        ```yaml
        templates:
          my_template:
            optional:
              - my_collection_poster
            tmdb_collection_details: <<value>>
            collection_order: release
            url_poster: <<my_collection_poster>>
        dynamic_collections:
          TMDb Collections:          # This name is the mapping name
            type: tmdb_collection
            remove_suffix: "Collection"
            template: my_template
            template_variables: #(1)!
              my_collection_poster: #(2)!
                119: https://www.themoviedb.org/t/p/original/oENY593nKRVL2PnxXsMtlh8izb4.jpg #(3)!
                531241: https://www.themoviedb.org/t/p/original/nogV4th2P5QWYvQIMiWHj4CFLU9.jpg #(4)!
        ```

        1. Template variables are placed under `template_variables`.
        2. `my_collection_poster` is the template variable being changed.
        3. For key `119` use the url as the my_collection_poster template variable.
        4. For key `531241` use the url as the my_collection_poster template variable.

??? blank "`remove_suffix` - Used to remove the defined suffixes.<a class="headerlink" href="#remove-suffix" title="Permanent link">¶</a>"

    <div id="remove-suffix" />Used to remove the defined suffixes from the key before it’s used in the collection title.

    <hr style="margin: 0px;">
    
    **Attribute:** `remove_suffix`
    
    **Accepted Values:** List or comma-separated string of suffixes to remove

    ???+ example "Example"

        When using `type: tmdb_collection` you may not want every collection title to end with `Collection`.

        ```yaml
        dynamic_collections:
          TMDb Collections:          # This name is the mapping name
            type: tmdb_collection
            remove_suffix: "Collection"
        ```

??? blank "`remove_prefix` - Used to remove the defined prefixes.<a class="headerlink" href="#remove-prefix" title="Permanent link">¶</a>"

    <div id="remove-prefix" />Used to remove the defined prefixes from the key before it’s used in the collection title.

    <hr style="margin: 0px;">
    
    **Attribute:** `remove_prefix`
    
    **Accepted Values:** List or comma-separated string of prefixes to remove

    ???+ example "Example"

        When using `type: tmdb_collection` you may not want every collection title to start with `The`.

        ```yaml
        dynamic_collections:
          TMDb Collections:          # This name is the mapping name
            type: tmdb_collection
            remove_prefix: "The"
        ```

??? blank "`title_format` - Used to specify the format you want the collection titles to be.<a class="headerlink" href="#title-format" title="Permanent link">¶</a>"

    <div id="title-format" />Used to specify the format you want the collection titles to be.

    There are a few special tags you can include in the `title_format`:

    * `<<key_name>>` is **required** and is what will be replaced by the dynamic key name.

    * `<<limit>>` will be replaced the limit template variable if passed to the definition.

    * `<<library_type>>` will be replaced with either `movie`, `show`, `artist`, or `video` depending on your library 
    type.

    * `<<library_typeU>>` will be replaced with either `Movie`, `Show`, `Artist`, or `Video` depending on your library 
    type.

    <hr style="margin: 0px;">
    
    **Attribute:** `title_format`
    
    **Accepted Values:** String with `<<key_name>>` in it.

    ???+ example "Example"

        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: genre
            title_format: Top 50 <<key_name>> <<library_type>>s
        ```

??? blank "`key_name_override` - Used to override key names before being formatted into titles.<a class="headerlink" href="#key-name-override" title="Permanent link">¶</a>"

    <div id="key-name-override" />Defines how key names can be overridden before they are formatted into collection 
    titles.

    <hr style="margin: 0px;">
    
    **Attribute:** `key_name_override`
    
    **Accepted Values:** [Dictionary](../kometa/yaml.md#dictionaries) where the key is the key name you want to change and 
    the value is what to change that key name to. 

    ???+ example "Example"

        This example uses `key_name_override` to change the formatting of "France" to "French" so that a collection can 
        be named "French Cinema" instead of simply "France".
          
        * This particular example also uses the `title_format` attribute to manipulate the naming convention of the 
        collections.
        
        ```yaml
        dynamic_collections:
          Countries:         # mapping name does not matter, just needs to be unique
            type: country
            title_format: <<key_name>> Cinema
            key_name_override:
              France: French
        ```

??? blank "`title_override` - Used to override titles ignoring title formatting.<a class="headerlink" href="#title-override" title="Permanent link">¶</a>"

    <div id="title-override" />Defines how collection titles can be overridden ignoring title formatting.

    <hr style="margin: 0px;">
    
    **Attribute:** `title_override`
    
    **Accepted Values:** [Dictionary](../kometa/yaml.md#dictionaries) where the key is the `dynamic key` you want to change 
    and the value is what to change the title to. 

    ???+ example "Example"

        This example will override the TMDb Star Wars collection which has an TMDb ID of `10` with `Star Wars Universe.
        
        ```yaml
        dynamic_collections:
          TMDb Collections:          # mapping name does not matter, just needs to be unique
            type: tmdb_collection
            remove_suffix: "Collection"
            title_override:
              10: Star Wars Universe
        ```

??? blank "`custom_keys` - Used to allow the use of custom keys.<a class="headerlink" href="#custom-keys" title="Permanent link">¶</a>"

    <div id="custom-keys" />Defines if custom keys are allowed. **Defaults to `true`**

    <hr style="margin: 0px;">
    
    **Attribute:** `custom_keys`
    
    **Accepted Values:** `true` or `false`

    ???+ example "Example"

        ```yaml
        dynamic_collections:
          TMDb Collections:          # mapping name does not matter, just needs to be unique
            type: tmdb_collection
            remove_suffix: "Collection"
            custom_keys: false
        ```

??? blank "`test` - Used to run all collections in this set as tests.<a class="headerlink" href="#test" title="Permanent link">¶</a>"

    <div id="test" />Used to run all collections in this set with `test: true` in each collection definition. 
    **Defaults to `fales`**

    <hr style="margin: 0px;">
    
    **Attribute:** `test`
    
    **Accepted Values:** `true` or `false`

    ???+ example "Example"

        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: genre
            test: true
        ```

??? blank "`sync` - Used to remove dynamic collections that are no longer in the creation list.<a class="headerlink" href="#sync" title="Permanent link">¶</a>"

    <div id="sync" />Will remove dynamic collections that are no longer in the creation list. **Defaults to `fales`**

    ???+ warning
    
        The mapping name is added as a label to any collection created using this dynamic collection set and because of 
        this when `sync` is true all collections with that label not found in this run will be deleted.

    <hr style="margin: 0px;">
    
    **Attribute:** `sync`
    
    **Accepted Values:** `true` or `false`

    ???+ example "Example"

        ```yaml
        dynamic_collections:
          Trakt Liked Lists:          # mapping name does not matter just needs to be unique
            type: trakt_liked_lists
            sync: true
        ```

??? blank "`include` - Used to define a specific list of keys to be made into collections.<a class="headerlink" href="#include" title="Permanent link">¶</a>"

    <div id="include" />Define a list of keys to be made into collections. 

    ???+ warning
    
        This cannot be used with `exclude`.

    ???+ tip

        Use with the `other_name` attribute to create a catch-all collection for all keys not in the `include` list or 
        in any [`addons`](#addons) list.

    <hr style="margin: 0px;">
    
    **Attribute:** `include`
    
    **Accepted Values:** `true` or `false`

    ???+ example "Example"

        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: genre
            include:
              - Action
              - Adventure
              - Animation
              - Comedy
              - Family
              - Fantasy
              - Horror
              - Romance
              - Science Fiction
              - War
        ```

??? blank "`other_name` - Used to create an "other" collection.<a class="headerlink" href="#other-name" title="Permanent link">¶</a>"

    <div id="other-name" />Will create an "other" collection when also using the [`include`](#include) by specifying the
    "other" collection's name as `other_name`. When defined, all keys not in [`include`](#include) or 
    [`addons`](#addons) will be combined into this collection.

    <hr style="margin: 0px;">
    
    **Attribute:** `other_name`
    
    **Accepted Values:** String to make the "other" collection's name

    ???+ example "Example"

        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: genre
            other_name: Other Genres
            include:
              - Action
              - Adventure
              - Animation
              - Comedy
              - Family
              - Fantasy
              - Horror
              - Romance
              - Science Fiction
              - War
        ```

??? blank "`other_template` - Used to define which templates the dynamic other collection uses.<a class="headerlink" href="#other-template" title="Permanent link">¶</a>"

    <div id="other-template" />Used to define which templates are used for the dynamic other collection when they need 
    to be different from the regular collection templates.

    ???+ tip
    
        To use an other collection you must be using the [`include`](#include) and [`other_name`](#other-name) 
        attributes.

    Each template is passed a few template variables you can use.

    * `value`: The list of keys and addons

    * `key`: The dynamic key

    * `key_name`: The key after `key_name_override`, `remove_prefix`, or `remove_suffix` are run on it.

    * `included_keys`: The list of included keys

    * `used_keys`: The list of all keys used (included_keys and their addon keys)

    <hr style="margin: 0px;">
    
    **Attribute:** `other_template`
    
    **Accepted Values:** Name of template or list of templates to use for the other collection only

    ???+ example "Example"

        ```yaml
        templates: 
          Other:
            plex_search:
              any:
                genre: <key>
            summary: Other Genres found in the library.
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: genre
            other_name: Top Other Genres
            other_template: Other
            include:
              - Action
              - Adventure
              - Animation
              - Comedy
              - Family
              - Fantasy
              - Horror
              - Romance
              - Science Fiction
              - War
        ```

## Dynamic Collection Template Variables

When calling a collection file with dynamic collection all the following are automatically accepted as template 
variables which will just replace the same attribute when running the file.

* `data`
* `exclude`
* `addons`
* `remove_suffix`
* `remove_prefix`
* `title_format`
* `key_name_override`
* `title_override`
* `custom_keys`
* `test`
* `sync`
* `include`
* `other_name`

There are also several template variables that will be automatically append/remove from `data`, `exclude`, `include`, 
and `addons` so they can be changed by the user on the fly when needed.

* `append_data`
* `remove_data`
* `append_exclude`
* `remove_exclude`
* `append_include`
* `remove_include`
* `append_addons`
* `remove_addons`

{%
   include-markdown "./dynamic_examples.md"
%}