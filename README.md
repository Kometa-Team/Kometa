# Plex Meta Manager
#### Version 1.9.1

The original concept for Plex Meta Manager is [Plex Auto Collections](https://github.com/mza921/Plex-Auto-Collections), but this is rewritten from the ground up to be able to include a scheduler, metadata edits, multiple libraries, and logging. Plex Meta Manager is a Python 3 script that can be continuously run using YAML configuration files to update on a schedule the metadata of the movies, shows, and collections in your libraries as well as automatically build collections based on various methods all detailed in the wiki. Some collection examples that the script can automatically build and update daily include Plex Based Searches like actor, genre, or studio collections or Collections based on TMDb, IMDb, Trakt, TVDb, AniDB, or MyAnimeList lists and various other services.

The script can update many metadata fields for movies, shows, collections, seasons, and episodes and can act as a backup if your plex DB goes down. It can even update metadata the plex UI can't like Season Names. If the time is put into the metadata configuration file you can have a way to recreate your library and all its metadata changes with the click of a button.

The script is designed to work with most Metadata agents including the new Plex Movie Agent, New Plex TV Agent, [Hama Anime Agent](https://github.com/ZeroQI/Hama.bundle), and [MyAnimeList Anime Agent](https://github.com/Fribb/MyAnimeList.bundle).

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?business=JTK3CVKF3ZHP2&item_name=Plex+Meta+Manager&currency_code=USD) 

## Getting Started

1. Install Plex Meta Manager either by installing Python3 and following the [Local Installation Guide](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Local-Installation)
   or by installing Docker and following the [Docker Installation Guide](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Docker-Installation) or the [unRAID Installation Guide](https://github.com/meisnate12/Plex-Meta-Manager/wiki/unRAID-Installation).
2. Once installed, you have to create a [Configuration File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Configuration-File) filled with all your values to connect to the various services. 
3. After that you can start updating Metadata and building automatic Collections by creating a [Metadata File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Metadata-File) for each Library you want to interact with.
4. Explore the [Wiki](https://github.com/meisnate12/Plex-Meta-Manager/wiki) to see all the different Collection Builders that can be used to create collections. 

## Support

* Before posting on Github about an enhancement, error, or configuration question please visit the [Plex Meta Manager Discord Server](https://discord.gg/TsdpsFYqqm).
* If you're getting an Error or have an Enhancement post in the [Issues](https://github.com/meisnate12/Plex-Meta-Manager/issues).
* If you have a configuration question post in the [Discussions](https://github.com/meisnate12/Plex-Meta-Manager/discussions).
* To see user submitted Metadata configuration files, and you to even add your own, go to the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs).
* Pull Request are welcome but please submit them to the develop branch.
* If you wish to contribute to the Wiki please fork and send a pull request on the [Plex Meta Manager Wiki Repository](https://github.com/meisnate12/Plex-Meta-Manager-Wiki).
