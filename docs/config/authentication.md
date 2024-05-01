# Trakt and MyAnimeList Authentication

When trying to authorize Trakt or MyAnimeList, Kometa needs to run in interactive mode so that you can enter details. This is problematic on some setups [namely docker] where entering interactive mode is not always simple.

These scripts allow you to authorize Trakt and MyAnimeList here on the wiki. Once authorized, the script will give you a YAML block that you will copy into the config.yml, replacing the existing `trakt` and/or `myanimelist` sections.

The source code for these scripts can be found on the [Trakt-MAL-OAuth Repository](https://github.com/Kometa-Team/Trakt-MAL-OAuth).

## Usage

1.  Enter client ID and secret.
2.  For Trakt, if you didn't retrieve a PIN yourself less than ten minutes ago, click the button, and enter the PIN in the field.
3.  For MyAnimeList, click the button to authenticate and get the required "localhost URL"
4.  Click "Submit"
5.  Copy and paste the result into your Kometa config.

<iframe src="https://kometa-auth-2cb6c5672416.herokuapp.com/" width="100%" height="700" style="border:0px solid black;"></iframe>

## Running the Authentication Scripts Locally

For users who want full control over the scripts and would prefer the run them locally, you can run the script in docker or python by following the instructions in the [Trakt-MAL-OAuth Repository](https://github.com/Kometa-Team/Trakt-MAL-OAuth).

??? abstract "Click for instructions on how to run the scripts locally"

    Ensure you have downloaded a copy of the [Trakt-MAL-OAuth Repository](https://github.com/Kometa-Team/Trakt-MAL-OAuth). If you have downloaded the ZIP file, extract it to your desired location.

    {%    
      include-markdown "https://raw.githubusercontent.com/Kometa-Team/Trakt-MAL-OAuth/master/README.md"
      start="You can run it in Docker or Python."
    %}
    
