---
hide:
  - toc
---
{%
    include-markdown "./../../../templates/walkthrough/container.md"
    replace='{
        "CONTAINER": "Synology",
        "NAS_TYPE": "Synology"
    }'
%}

=== "DiskStation Manager v. 7.2"

    ## Container Manager

    1. Open the Package Center app from the Synology Web GUI.

        ![Prerequisite 1](./../../../assets/images/kometa/install/synology/dsm72-01.png)

    2. Type `docker` in the search bar and once it comes up, click "Install" next to Container Manager if it isn't already installed. 
       Then click "Open" to bring up the Container Manager.

        ![Prerequisite 2](./../../../assets/images/kometa/install/synology/dsm72-02.png)

    3. Click "Open" to bring up the Container Manager.

        ![Prerequisite 2](./../../../assets/images/kometa/install/synology/dsm72-03.png)

    ## Creating the Kometa container

    1. Click the registry tab, type "Kometa" in the search bar, and select the `kometateam/kometa` image.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-04.png)

    2. When you click the image, a popup will appear where you can choose the tag [version of the image] you want to use. Most likely, this is `latest`. 
       If you need to use one of these other tags, you would choose it here. Once you choose a tag, click 'Apply'.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-05.png)

    3. The image will be downloaded, which shouldn't take long.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-06.png)

    3. Once the download completes, click on the "Container" tab. Click "create" to create a new container.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-07.png)

    4. This will bring up the container creation wizard.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-08.png)

    5. Click the top UI element and choose the image you downloaded.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-09.png)

    6. Enter a name, and check the "auto-start" box.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-10.png)

        NOTE: The name you enter here is the name of the container, not the name of the image. You can name it whatever you want.

        IMPORTANT: If you are creating an image that you will be configuring to run immediately, you should NOT check the "auto-start" box. 
        That will cause the container to loop endlessly. If you don't know what this means yet, check the box.

        Click Next.

    7. On this screen, you'll create the one volume map that Kometa requires.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-11.png)

        Click "Add Folder" under "Volume Settings".

    8. Click "docker".

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-12.png)

    9. Click "Create Folder" and enter a name.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-13.png)

        Click "OK".

    10. Make sure the folder you just created is selected, and click "Select".

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-14.png)

    11. Enter `/config` in the box in the middle of the pane. Enter *exactly that*, no more, no less.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-15.png)

    12. There is one setting here that you *may* need to change, and only you know if you do. Scroll down to the network settings. 
        Depending on where Plex is running, you may need to change this from "bridge" to "host". If you don't know what this means, you probably don't need to change it.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-16.png)

          Click "Next".

    13. You're presented with a summary of the things you've done so far. Click "Done"

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-17.png)

    14. You will probably be presented with a bunch of errors; these are expected. Kometa cannot find the config file it needs, so it will fail to start. 
        The auto-start setting you checked earlier is making it try over and over. This is normal.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-18.png)

    15. If you click on the container, then on the log tab, you will see this specific error.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-19.png)

    ## Adding the Kometa config file.

    This is where you need the `config.yml` that you created with the walkthrough earlier.

    1. Open File Station. In the sidebar, expand the "docker" item and click on the folder you created earlier.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-20.png)

    2. At the top of hte window, click "Upload" and choose "Upload -> Overwrite".

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-21.png)

    3. Navigate to the `config.yml` file you created earlier and click "Upload". The file will appear in the list.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-22.png)

    4. You will note that the errors have stopped. If you go back to Container Manager, you will see that the container is running.

        ![Step 1](./../../../assets/images/kometa/install/synology/dsm72-23.png)
    
    At this point, Kometa is waiting until 5AM to wake up and process the config file.

=== "Some unidentified older version"

    ## Prerequisite: Installing Docker

    1. Open the Package Center app from the Synology Web GUI.

        ![Prerequisite 1](./../../../assets/images/kometa/install/synology/synology-01.png)

    2. Type `docker` in the search bar and once it comes up, click "Install" to add Docker. Then click "Open" to bring it up.

        ![Prerequisite 2](./../../../assets/images/kometa/install/synology/synology-02.png)

    ## Installing Kometa

    1. Open the Docker app.

        ![Step 1](./../../../assets/images/kometa/install/synology/synology-03.png)

    2. Search and Download the Image.

        1. Click Registry.
        2. Search for `kometateam/kometa`.
        3. Select the Repository.
        4. Click Download.

        ![Step 2](./../../../assets/images/kometa/install/synology/synology-04.png)

    3. Select the tag you want to run from the dropdown and click "Select."

        The options are:

        - `latest` - most recent official release; typically the most stable.
        - `develop` - development release, contains new features that haven't made it to latest yet, but may have minor problems.
        - `nightly` - bleeding-edge development version; latest fixes go here, but breakage should be expected.

        ![Step 3](./../../../assets/images/kometa/install/synology/synology-05.png)

    4. Select the Image and Create a Container.

        1. Click Image.
        2. Select the `kometateam/kometa` Image.
        3. Click Launch.

        ![Step 4](./../../../assets/images/kometa/install/synology/synology-06.png)

    **From this point on the setup looks a little different depending on if the Synology is running DiskStation Manager 7 or DiskStation Manager 6.**

    === "DiskStation Manager 7"

        5. Specify your docker network type. Then click "Next".

            ![](./../../../assets/images/kometa/install/synology/dsm7-01.png)

        6. You can name the Container whatever you want using the "Container Name" text Box.

            ![](./../../../assets/images/kometa/install/synology/dsm7-02.png)

        7. To add Environment Variables and Command Line Arguments click "Advanced Settings". (Optional)

            Information on available Command Line Arguments and Environment Variables can be found [here](../environmental.md)

            To add an Environment Variable click "Environment" then click Add" and then fill in the Variable and Value.

            ![](./../../../assets/images/kometa/install/synology/dsm7-03.png)

            To use Command Line Arguments click "Execution Command" put the arguments in the "Command" text field.

            ![](./../../../assets/images/kometa/install/synology/dsm7-04.png)

            Click "Save" to save the settings and go back to the General Settings Screen.

        8. Click "Next" from the General Settings Screen to get to the Port Settings Screen where you just want to click "Next" as Kometa has no Ports.

            ![](./../../../assets/images/kometa/install/synology/dsm7-05.png)

        9. Next we need to add your config folder to the container. From the Volume Settings Screen click "Add Folder".

            ![](./../../../assets/images/kometa/install/synology/dsm7-06.png)

        10. Select from your Synology File System where you want to store your Kometa config files and then enter `/config` as the "Mount path". 
            Then click "Next" to go to the Summary Page.

            ![](./../../../assets/images/kometa/install/synology/dsm7-07.png)

        11. From the Summary Page select "Done" to finish and creating the container.

            ![](./../../../assets/images/kometa/install/synology/dsm7-08.png)

    === "DiskStation Manager 6"

        5. You can name the Container whatever you want using the "Container Name" text Box. Then click "Advanced Settings".

            ![](./../../../assets/images/kometa/install/synology/dsm6-01.png)

        6. Next we need to add your config folder to the container. Select the "Volume" Tab, click "Add Folder," 
           and select from your Synology File System where you want to store your Kometa config files.

            ![](./../../../assets/images/kometa/install/synology/dsm6-02.png)

        7. Enter `/config` as the "Mount Point."

            ![](./../../../assets/images/kometa/install/synology/dsm6-03.png)

        8. Select the "Environment" Tab. (Optional)
    
            Environment Variables and Command Line Arguments can be added here.

            - To add an Environment Variable Click "Add" and then fill in the Variable and Value.
            - To use Command Line Arguments put the arguments in the "Command" text field.

            Information on available Command Line Arguments and Environment Variables can be found [here](../environmental.md)

            ![](./../../../assets/images/kometa/install/synology/dsm6-04.png)

        9. Select "Apply" to save the "Advanced Settings," select "Next" to go to the Summary, and select "Done" to finish and create the container.

            ![](./../../../assets/images/kometa/install/synology/dsm6-05.png)
