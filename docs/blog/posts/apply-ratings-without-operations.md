---
title: "Apply Ratings Overlays without using Operations"
date:
    created: 2024-09-12
authors:
    - yozora
    - chaz
categories:
    - Announcements
    - Defaults
    - Overlays
---

![Ratings GIF](https://mir-s3-cdn-cf.behance.net/project_modules/hd/8bfb74111957539.600b408feb79c.gif){ align=right itemprop="image" }

**Say goodbye to using Operations to update your ratings, and say hello to quicker rating overlays!**

We've been hard at work in the background trying to simplify the process for applying ratings to posters, and we're ready to introduce a feature we call "Direct Ratings".

Direct Ratings allows Kometa to fetch the ratings from the source (such as IMDb, TMDb, Rotten Tomatoes via MDBList, etc.) during the Overlay process, completely bypassing the need to use Mass Rating Update operations to fetch and apply the ratings into the three Plex ratings slots.

We are hoping that this new process will help to reduce your runtimes and allow you to get right to the good stuff.

<!-- more -->


## What's Changed?

In previous versions of Kometa, you had three slots in Plex (user, critic, audience) which you could use as placeholders for the ratings that you wanted to show as Overlays. For example, you could use the `Mass Audience Rating Update` to place the Metacritic rating into the Audience slot, and then use that data to feed your overlays so that the Audience rating is associated with the Metacritic image.

This was a tedious process that limited the user to having 3 ratings shown on their poster, and required operations to run and check for any rating updates prior to the Overlay application process.

Our new system bypasses this process by completely detaching the ratings applied on Overlays from the slots within Plex. You no longer need to use Operations, you can simply tell Kometa to fetch the rating you want and apply it as an overlay.

### How does it work?

Below is an example of the old and new system of using the `- default: ratings` file to apply the TMDb, IMDb and Rotten Tomatoes Audience score to a library:

=== "Previous Process"

    ```yaml
    libraries:
      Movies:
        operations:
          mass_user_rating_update: tmdb
          mass_audience_rating_update: imdb
          mass_critic_rating_update: mdb_tomatoesaudience
        overlay_files:
          - default: ratings
            template_variables:
              rating1: user
              rating1_image: tmdb
              rating2: audience
              rating2_image: imdb
              rating3: critic
              rating3_image: rt_popcorn
    ```

=== "New Process"

    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: ratings
            template_variables:
              rating1: tmdb
              rating2: imdb
              rating3: mdb_tomatoesaudience
    ```

As you can see from the new process, the operations have completely disappeared from the process. Additionally, you no longer have to specify what image you want to use; Kometa will automatically select the most appropriate image to use based on your rating source, for example using the IMDb logo if your rating source is `imdb`

### Can I still use the old method?

Absolutely, this is not a breaking change and if you want to continue to use the Mass Rating Update operations method then you can continue to do so, we have no plans to retire the old method.

If you do want to switch to the new method, there are some drawbacks that we want to be upfront about:

- The new process will only work for Movies and Shows, it does not work at the Season or Episode level. You can still use the new method for Shows and Movies, but you will have to continue using the old method for any Season and Episode-level rating overlays.
- Due to the way that the ratings are now pulled down, the default file can no longer show the "Fresh" or "Rotten" image for Rotten Tomatoes based upon the score that a particular movie/show has, this is because the ratings is pulled down too late in the overlay process for us to be able to add logic to check what the number is.
    - To combat this, we've created new images for Rotten Tomatoes Audience and Critic ratings which you can see here:

    ![RT-Aud-Direct.png](../images/RT-Aud-Direct.png) ![RT-Crit-Direct.png](../images/RT-Crit-Direct.png)

### Can I use the system for my own overlays?

Absolutely, this update is not specific to the ratings Default file, it can be used on any rating overlay.

A full list of the available Ratings Text can be found [here](../../files/overlays.md#special-rating-text)

An added benefit is that you are no longer limited to 3 ratings, as you can see here I have added 5 ratings to my overlays:

![5 Overlays](https://media.discordapp.net/attachments/929901956271570945/1222537162944417842/image.png?ex=66e43d75&is=66e2ebf5&hm=176c744442389ec0a858882d1b760acc19222a1403ea03009009a95065f2bba7&=&format=webp&quality=lossless)

```yaml
overlays:
  backdrop:
    overlay:
      name: backdrop
      back_color: "#00000099"
      back_height: 500
      vertical_position: top
    plex_all: true
  mytext:
    overlay:
      name: text(tmdb_rating is <<tmdb_rating>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 30
      vertical_align: top
      font_size: 63
      font_color: "#FFFFFF"
    plex_all: true
  mytext2:
    overlay:
      name: text(mdb_letterboxd_rating% is <<mdb_letterboxd_rating%>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 130
      vertical_align: top
      font_size: 63
      font_color: "#FFFFFF"
    plex_all: true
  mytext3:
    overlay:
      name: text(mdb_tmdb_rating# is <<mdb_tmdb_rating#>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 230
      vertical_align: top
      font_size: 63
      font_color: "#FFFFFF"
    plex_all: true
  mytext4:
    overlay:
      name: text(mdb_tomatoes_rating/ is <<mdb_tomatoes_rating/>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 330
      vertical_align: top
      font_size: 63
      font_color: "#FFFFFF"
    plex_all: true
  mytext5:
    overlay:
      name: text(imdb_rating is <<imdb_rating>>)
      horizontal_offset: 0
      horizontal_align: center
      vertical_offset: 430
      vertical_align: top
      font_size: 63
      font_color: "#FFFFFF"
    plex_all: true
```