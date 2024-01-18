# Trakt and MyAnimeList Authentication

When trying to authorize Trakt or MyAnimeList, PMM needs to run in interactive mode so that you can enter details. This is problematic on some setups [namely docker] where entering interactive mode is not always simple.

These scripts allow you to authorize Trakt and MyAnimeList here on the wiki. Once authorized, the script will give you a YAML block that you will copy into the config.yml, replacing the existing `trakt` and/or `myanimelist` sections.

The source code for these scripts can be found on [Chazlarson's GitHub Repository](https://github.com/chazlarson/PMM_Auth)
## Usage

1.  Enter client ID and secret.
2.  For Trakt, if you didn't retrieve a PIN yourself less than ten minutes ago, click the button, and enter the PIN in the field.
3.  For MyAnimeList, click the button to authenticate and get the required "localhost URL"
4.  Click "Submit"
5.  Copy and paste the result into your PMM config.

<iframe src="https://pmm-auth-8e685ca9b226.herokuapp.com/" width="100%" height="700" style="border:0px solid black;"></iframe>

## Running the Authentication Scripts Locally

For users who want full control over the scripts and would prefer the run them locally, you can run the script in docker or python by downloading the scripts from [Chazlarson's GitHub Repository](https://github.com/chazlarson/PMM_Auth)

??? abstract "Click for instructions on how to run the scripts locally"

    Ensure you have downloaded a copy of the script from [Chazlarson's GitHub Repository](https://github.com/chazlarson/PMM_Auth). If you have downloaded the ZIP, extract it to your desired location.

    {%    
      include-markdown "https://raw.githubusercontent.com/chazlarson/PMM_Auth/main/README.md"
      start="You can run it in Docker or Python."
    %}
    
