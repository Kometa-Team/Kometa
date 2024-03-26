# Templates

Collection, Playlist, Metadata, and Overlay Files often share a lot of common or generalizable configuration details. 
Templates allow you to define these details in order for them to be used across multiple definitions.

Templates definitions are placed under the top level attribute `templates`. The `templates` top level attribute and its 
templates can either be defined in the same file as the other definitions or from an external file using the top level 
`external_templates` attribute. See [File Blocks](../config/files.md) for how to define files for `external_templates`.

??? example "External Template Example (click to expand)"

    In this example this is a file in your config folder called `my_templates.yml`.

    ```yaml
    templates:
      Actor:
        plex_search:
          all:
            actor: tmdb
        tmdb_person: <<person>>
        sort_title: "!_<<collection_name>>"
        sync_mode: sync
        collection_order: release
    ```

    This is a Collection File in your config folder called `actors.yml`.

    ```yaml
    external_templates:
     - file: config/my_templates.yml       
    collections:
      Bruce Lee:
        template: {name: Actor, person: 19429}
      Chris Pratt:
        template:
          name: Actor
          person: 73457
    ```

## Template Definition

Inside a template definition, you can use all the [Builders](builders/overview.md), [Filters](filters.md), 
[Settings](settings.md), [Updates](updates.md), and [Item Updates](item_updates.md) attributes that you can give 
collections/playlists [except `template`; templates cannot be nested].

In addition, templates also have a few special attributes that they can use:

??? blank "`default` - Sets what template variables default to.<a class="headerlink" href="#default" title="Permanent link">¶</a>"

    <div id="default" />The `default` attribute allows default values for template variables to be used if they're not 
    specified in the call. It's value is a dictionary of key value pairs where the key is the template variable and the 
    value is the default value to set it to when not provided.

    **A variable cannot be default if it is a conditional variable.**

    ???+ example "Example"

        Click the :fontawesome-solid-circle-plus: icon to learn more

        ```yaml
        templates:
          Actor:
            default:
              my_sync_mode: sync #(1)!
            plex_search:
              all:
                actor: tmdb
            tmdb_person: <<person>>
            sort_title: "!_<<collection_name>>"
            sync_mode: <<my_sync_mode>> #(2)!
            collection_order: release
        collections:
          Bruce Lee:
            template:
              name: Actor
              person: 19429
              my_sync_mode: append #(3)!
          Chris Pratt:
            template: #(4)!
              name: Actor
              person: 73457
        ```
        
        1. This sets the default value of the template variable `my_sync_mode` to `sync`.
        2. The value for template variable `my_sync_mode` will replace `<<my_sync_mode>>` here.
        3. This specifiys that `my_sync_mode` for this definition will be `append`.
        4. Since `my_sync_mode` is not passed to this definition the value of `my_sync_mode` will be the default `sync`.

??? blank "`optional` - List of template variables to be removed when not provided.<a class="headerlink" href="#optional" title="Permanent link">¶</a>"

    <div id="optional" />The `optional` attribute can specify variables that when not specified on the template call 
    will cause any attribute using one of those variables to be ignored in the template. It's value is a list of 
    template variables to be considered optional.

    **You can make any template variable optional per collection by setting it to `null`.**

    **A variable cannot be optional if it is a conditional variable or has a default value.**

    ???+ example "Example"

        Click the :fontawesome-solid-circle-plus: icon to learn more

        ```yaml
        templates:
          Actor:
            optional:
              - my_sync_mode #(1)!
            plex_search:
              all:
                actor: tmdb
            tmdb_person: <<person>>
            sort_title: "!_<<collection_name>>"
            sync_mode: <<my_sync_mode>> #(2)!
            collection_order: release
        collections:
          Bruce Lee:
            template:
              name: Actor
              person: 19429
              my_sync_mode: append #(3)!
          Chris Pratt:
            template: #(4)!
              name: Actor
              person: 73457
        ```
        
        1. This sets the template variable `my_sync_mode` as an optional variable.
        2. The value for template variable `my_sync_mode` will replace `<<my_sync_mode>>` here or removed as optional.
        3. This specifiys that `my_sync_mode` for this definition will be `append`.
        4. Since `my_sync_mode` is not passed to this definition it will ignore the entire `sync_mode` attribute in the 
        template.

??? blank "`conditionals` - Can set template variables based on other template variables.<a class="headerlink" href="#conditionals" title="Permanent link">¶</a>"

    <div id="conditionals" />Each conditional is identified by its mapping name under the top level `conditionals` 
    attribute can have these attributes:

    |  Attribute   | Description                                                                                                                                                                                                                                                      |
    |:------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `conditions` | A list of condition blocks where if all conditions are met then the variable will be the `value` specified in that condition block. Once all conditions in a block are met, that `value` will be used and no other blocks will be run.<br>**This attribute is required** |
    |  `default`   | The default value for when no condition block is met. If default is not specified the variable becomes an optional variable.<br>**This attribute is optional**                                                                                                         |
    
    #### Condition Blocks

    A condition block consists of one or more key value pairs comparing given template variables to pre supplied static 
    values. 

    The key is the name of the template variable who's value you want to compare. While the value is the staic value or 
    values to compare aginst. Every condition block must also have the `value` key which will be the value of the 
    template variable if all the conditions in that block are met.

    There are three ways to compare values:

    1. Using no modifier:

        * The given template variable's value must equal the static value or be in the list of static values.

    2. Using the not modifier by appending `.not` to the key template variable:

        * The given template variable's value must not equal the static value or not be in the list of static values.

    3. Using the exists modifier by appending `.exists` to the key template variable:

        * While `true` the template variable specified must exist in the template call.
        * While anything but `true` the template variable specified must not exist in the template call.

    ???+ example "Example"

        Click the :fontawesome-solid-circle-plus: icon to learn more

        ```yaml
        templates:
          CustomTemplate:
            conditionals: #(1)!
              offset: #(2)!
                default: 15 #(3)!
                conditions: #(4)!
                  - align.exists: false #(5)!
                    value: 150
                  - align: center #(6)!
                    value: 0
                  - align: [top, bottom] #(7)!
                    value: 15
              key_name: #(8)!
                conditions: #(9)!
                  - style: standards #(10)!
                    key: 1080
                    value: Full HD
                  - style: standards #(11)!
                    key: 4k
                    value: Ultra HD
        ```

        1. This is the main `conditionals` attribute to start the whole seciton.
        2. This is the main mapping of the conditional template variable `offset`.
        3. This sets the default variable of `offset` to `15`.
        4. This is the base attribute for the condition blocks.
        5. If the variable `align` is not provided to the template then set the variable to `150`.
        6. If the variable `align` is passed with the value `center` then set the variable to `0`.
        7. If the variable `align` is passed with the value `top` or `bottom` then set the variable to `15`.
        8. This is the main mapping of the conditional template variable `key_name`.<br><br>Since `default` is not used 
        `key_name` will be added to the optional variable list.
        9. This is the base attribute for the condition blocks.
        10. If the variable `style` is passed with the value `standards` and the variable `key` is passed with the value 
        `1080` then set the variable to `Full HD`.
        11. If the variable `style` is passed with the value `standards` and the variable `key` is passed with the value 
        `4k` then set the variable to `Ultra HD`.

??? blank "`move_prefix` - List of prefixes to move to the end of the collection/playlist name for sorting.<a class="headerlink" href="#move-prefix" title="Permanent link">¶</a>"

    <div id="move-prefix" />The `move_prefix` attribute can be used to specify a list or comma-separated string of 
    prefixes to move to the end of the collection/playlist name for sorting. This changes the template variables
    `collection_sort`, `playlist_sort`, and `mapping_sort`.

    ???+ example "Example"

        If you have `move_prefix: The, A, An` and a collection is called `The Avengers` then `<<collection_sort>>` is 
        replaced with `Avengers, The` instead of `The Avengers` for that collection, but the collection `Iron Man` will
        still just be `Iron Man`.

        ```yaml
        templates:
          Movies:
            move_prefix: The, A, An
            tmdb_collection: <<tmdb_id>>
            sort_title: <<collection_sort>>
            collection_order: release
        collections:
          The Avengers:
            template:
              name: Movies
              tmdb_id: 86311
          Iron Man:
            template:
              name: Movies
              tmdb_id: 131292
        ```

Every template also has access to these template variables:

* Either `<<collection_name>>`, `<<playlist_name>>`, or `<<overlay_name>>` which is the name of the definition.
* `<<mapping_name>>` is the original mapping name for the definition in the YAML file.
* Either `<<collection_sort>>` or `<<playlist_sort>>` which is the name of the definition after `move_prefix` is applied.
* `<<mapping_sort>>` which is the original mapping name for the definition after `move_prefix` is applied.
* `<<library_type>>` which is the library type (`movie`, `show`, `artist`, `video`).
* `<<library_name>>` which is the name of the library.
* All template variables can append `_encoded` to the variable name to use a URL encode version of the variable. ex. 
`<<collection_name_encoded>>`

## Template Call

To call a template from a definition you use the `template` attribute with the `name` attribute under it. Any attribute 
besides `name` under `template` is considered a template variables which are used to define the data that going to be 
changing in the template.

???+ tip

    The name of the template and the template variable names that you define are arbitrary, but they must match exactly 
    between the template definition and the template call.

### Template Name

The `name` attribute is what tells the template call which template to use. Its value must correspond exactly to the 
template mapping name you want to call. 

??? example "Template Name Example (click to expand)"
    
    This is an example using the template name `Actor` showing the template being called in two different ways.
    
    ```yaml
    templates:
      Actor: #(1)!
        plex_search:
          all:
            actor: tmdb
        tmdb_person: <<person>>
        sort_title: "!_<<collection_name>>"
        sync_mode: sync
        collection_order: release
    collections:
      Bruce Lee:
        template: {name: Actor, person: 19429} #(2)!
      Chris Pratt:
        template:
          name: Actor #(3)!
          person: 73457
    ```

    1. This defines the template name as `Actor`.
    2. This calls the `Actor` template using inline YAML syntax.
    3. This calls the `Actor` template using a more readable YAML syntax.

### Template Variables

Any other attribute aside from `name` under `template` is considered a template variable whose name must correspond 
exactly with the template variable name surrounded by `<<` and `>>` in the template definition. These template variables
will replace any part of any value that contains the template variable name surrounded by `<<` and `>>` in the template 
with the specified template variable's value.

??? example "Template Variables Example (click to expand)"
    
    This is an example using the template name `Actor` showing the template being called in two different ways.
    
    ```yaml
    templates:
      Actor:
        plex_search:
          all:
            actor: tmdb
        tmdb_person: <<person>> #(1)!
        sort_title: "!_<<collection_name>>"
        sync_mode: sync
        collection_order: release
    collections:
      Bruce Lee:
        template: {name: Actor, person: 19429} #(2)!
      Chris Pratt:
        template:
          name: Actor
          person: 73457 #(3)!
    ```

    1. The template variable `person` will replace `<<person>>` here.
    2. This calls the `Actor` template with the template variable `person` set to `19429` using inline YAML syntax.
    3. This calls the `Actor` template with the template variable `person` set to `73457` using a more readable YAML syntax.

### Multi-Template Variables

When using multiple Templates in a single definition you can send the same variable to all templates by using the 
`variables` attribute.

??? example "Multi-Template Variables Example (click to expand)"

    ```yaml
    templates:
      Actor:
        plex_search:
          all:
            actor: tmdb
        tmdb_person: <<person>>
        sort_title: "!_<<collection_name>>"
      Common:
        summary: "Movies that <<collection_name>> (TMDb ID: <<person>>) are in"
        sync_mode: sync
        collection_order: release
    collections:
      Bruce Lee:
        variables: {person: 19429}
        template: [{name: Actor}, {name: Common}]
      Chris Pratt:
        variables:
          person: 19429
        template:
         - name: Actor
         - name: Common
    ```

## Template Example

For this example were trying to create a template for all our various Actor/Actress Collections to save space in the 
YAML file and allow easier changes to all the Collections at once.

This is the example Collection File we're going to convert to using templates.

```yaml
collections:
  Bruce Lee:
    plex_search:
      all:
        actor: tmdb
    tmdb_person: 19429
    sort_title: "!_Bruce Lee" #(1)!
    sync_mode: sync
    collection_order: release
  Chris Pratt:
    plex_search:
      all:
        actor: tmdb
    tmdb_person: 73457
    sort_title: "!_Chris Pratt" #(2)!
    sync_mode: sync
    collection_order: release
```

1. This is wrapped in quotes because it contains a character [`!`] which has 
[syntactic meaning in YAML files](../pmm/yaml.md#string-literals). This "quoting special characters" is a general YAML 
requirement, not something specific to `sort_title`.
2. This is wrapped in quotes because it contains a character [`!`] which has 
[syntactic meaning in YAML files](../pmm/yaml.md#string-literals). This "quoting special characters" is a general YAML requirement, not something 
specific to `sort_title`.

You can continue adding definitions this way, but there's a lot of repetition there. Both of these collections have the 
same `sync_mode`, `collection_order`, and `actor` settings; the other two details, `tmdb_person` and `sort_title`, 
depend on a value defined in the collection.

Those repetitive aspects can be moved into a template and leveraged by multiple collections. For this example it might
look something like this:

```yaml
templates:
  Actor:
    plex_search:
      all:
        actor: tmdb
    tmdb_person: <<person>>
    sort_title: "!_<<collection_name>>"
    sync_mode: sync
    collection_order: release
```

The only things that change are the ID that is used with `tmdb_person` and the name of the collection that is used 
in `sort_title`.

Those two things surrounded by `<< >>` are "template variables" that you can define for any collection using this 
template, like this:

```yaml
collections:
  Chris Pratt:
    template:
      name: Actor
      person: 73457
```

or to do it in a single line you can do this 

```yaml
collections:
  Bruce Lee:
    template: {name: Actor, person: 19429}
```

Note that we provide the template name `Actor` and the value to insert in the place of `<<person>>`. The 
`<<collection_name>>` is a template variable that is always available and doesn't have to be called out like 
`<<person>>`.

Here's the full example Actor template and two different ways to use it, as it would appear in a collection file.

```yaml
templates:
  Actor:
    plex_search:
      all:
        actor: tmdb
    tmdb_person: <<person>>
    sort_title: "!_<<collection_name>>"
    sync_mode: sync
    collection_order: release
collections:
  Bruce Lee:
    template: {name: Actor, person: 19429}
  Chris Pratt:
    template:
      name: Actor
      person: 73457
```

## Advanced Example

Here's an example IMDb Genre template and two different ways to call it.

```yaml
templates:
  IMDb Genre:
    default:
      title: feature
      limit: 100
    optional:
      - poster_id
    imdb_search:
      type: movie
      release.after: 1989-12-31
      rating.gte: 5.0
      votes.gte: 10000
      genre.any: <<genre>>
      limit: <<limit>>
    sort_title: "!_<<collection_name>>"
    url_poster: https://theposterdb.com/api/assets/<<poster_id>>
    sync_mode: sync
    collection_order: alpha
collections:
  Action:
    template:
      name: IMDb Genre
      genre: action
    summary: Action film is a genre wherein physical action takes precedence in the storytelling. The film will often have continuous motion and action including physical stunts, chases, fights, battles, and races. The story usually revolves around a hero that has a goal, but is facing incredible odds to obtain it.
  Comedy:
    template: {name: IMDb Genre, genre: comedy, poster_id: 69200}
    summary: Comedy is a genre of film that uses humor as a driving force. The aim of a comedy film is to illicit laughter from the audience through entertaining stories and characters. Although the comedy film may take on some serious material, most have a happy ending. Comedy film has the tendency to become a hybrid sub-genre because humor can be incorporated into many other genres. Comedies are more likely than other films to fall back on the success and popularity of an individual star.
  Romantic Comedy:
    template: {name: IMDb Genre, genre: "romance,comedy", limit: 200}
    summary: Romantic Comedy is a genre that attempts to catch the viewer’s heart with the combination of love and humor. This sub-genre is light-hearted and usually places the two protagonists in humorous situation. Romantic-Comedy film revolves around a romantic ideal, such as true love. In the end, the ideal triumphs over the situation or obstacle, thus creating a happy ending.
    filters:
      genre: Comedy
```

Check out the example files in the 
[Plex Meta Manager Configs Repository](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12) 
for more uses and examples.
