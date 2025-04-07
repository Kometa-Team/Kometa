---
hide:
  - toc
---
{%
    include-markdown "./../../../templates/walkthrough/container.md"
    replace='{
        "CONTAINER": "QNAP \"Container Station\"",
        "NAS_TYPE": "QNAP"
    }'
%}

=== "Container Station v. 3.0.5.623"

    1. Open Container Station; click “Images”
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-01.png) 
    
    2. Select “Pull” from the top-right
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-02.png) 
    
    3. Leave Mode set to “Basic Mode”
       
        For the Registry select “Docker Hub”
           
        Under the "Image" section you will be typing in the name and version of the docker image you wish to pull. Type in the image you wish to use as follows:
    
        ```shell { .no-copy }
        kometateam/kometa:latest
        kometateam/kometa:develop
        kometateam/kometa:nightly
        ```

    4. Then click Pull.
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-03.png) 
    
        Note: You can repeat this step for each of the different versions and you’ll end up with this:
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-03a.png) 
    
        After the pull is complete the image(s) will now be available for use.
    
    5. From the "Images" menu under the "Actions" column click the "play" button to bring up the “Create Container” option.
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-04.png) 
    
    6. "Create Container" Step 1: "Select Image" – you’ve already done this so just click "Next". 
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-05.png) 
    
    7. "Create Container" Step 2: "Configure Container" - you can edit the name if you wish. 
       From here on you’ll be working in the Advanced Settings sub-menu. Click on "Advanced Settings".
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-06.png) 
    
    8. You can add [command-line switches](../../../environmental) to the "Command" field here. Do not edit the "Entrypoint" field.
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-07.png) 
    
        For example, if you wanted to run the collections you have defined as tests, add the `--run-tests` command-line flag:
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-08.png) 
    
        Generally speaking, editing these is not recommended as it is easy to render the container non-functional by doing so.
    
        It is more typical in Docker contexts to set these things with environment variables.
    
        Anything you can do via command-line arguments can be done with [Environment Variables](../../../environmental), which is more typical in Docker environments.
    
        For example, you could add an environment variable named `KOMETA_TESTS` with a value of `true` to run the collections you have defined as tests.
    
        Click "Environments" on the left to set environment variables.
    
    8. Select "Storage":
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-09.png) 
    
    9. Click the Trash Can icon to remove the default Storage Mapping:
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-10.png) 
    
    10. Click "Add Volume" then choose “Bind Mount Host Path”:
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-11.png) 
    
    11. Select the Yellow Folder icon
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-12.png) 
    
        “Select Host Path” will appear as seen below, letting you select the folder you want to use. 
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-13.png) 
    
        After selecting your folder and choosing "Apply" the "Host" path will be filled in. For the "Container" path you MUST use `/config`:
    
        ![](./../../../assets/images/kometa/install/qnap/qnap3-14.png)
    
    12. Select Next to advance to “Step 3 Summary”
    
    13. Select Finish

    This code will create a tabbed content section with the provided content, correctly indented and numbered, in your MkDocs documentation.

=== "Container Station v. unknown"

    1. Open Container Station; click "Create" in the left column.
    
        ![](./../../../assets/images/kometa/install/qnap/qnap1.png)

    2. Search for `kometateam/kometa`.

        On the "Docker Hub" tab you should see the image; click on it and click "Install".
        
        ![](./../../../assets/images/kometa/install/qnap/qnap2.png)

    3. Select the version you want to run from the dropdown and click "Next".

        The options are:
        - `latest`: most recent official release; typically the most stable
        - `develop`: development release, contains new features that haven't made it to latest yet, but may have minor problems
        - `nightly`: bleeding-edge development version; latest fixes go here, but breakage should be expected.

        ![](./../../../assets/images/kometa/install/qnap/qnap3.png)

    4. Change the container name if you wish.

        Command line arguments can be entered in the "Entrypoint" field after `/tini -s python3 kometa.py --`  

        IMPORTANT: **DO NOT REMOVE** ANY ELEMENT OF THAT TEXT. DO NOT ENTER ANYTHING INTO THE "Command" FIELD.

        For example, you could enter the following into the "Entrypoint" field to make Kometa run immediately when the container starts up: `/tini -s python3 kometa.py -- --run`

        Typically, in a Docker environment, this sort of thing is done via Environment Variables [the next step here]. 
        Editing the "Entrypoint" is not recommended, as it's easy to render the container non-functional if you are not sure what you're doing.

        Information on available command line arguments can be found [here](../../../environmental)

        Click "Advanced Settings >>"

        ![](./../../../assets/images/kometa/install/qnap/qnap4.png)

    5. Environment Variables can be added here:

        Anything you can do via command-line arguments can be done with Environment Variables, which is more typical in Docker environments.

        For example, you could add an environment variable named `KOMETA_RUN` with a value of `True` to make Kometa run immediately when the container starts up.

        Information on available Environment Variables can be found [here](../../../environmental)

        ![](./../../../assets/images/kometa/install/qnap/qnap5.png)

    6. Click Shared Folders Tab:

        Click "Add" in the middle section "Volume from host".

        "Volume from host" is the location on your QNAP where you want to store the config files.

        "Mount Point" must be `/config`

        When finished, click "Create".

        ![](./../../../assets/images/kometa/install/qnap/qnap7.png)
