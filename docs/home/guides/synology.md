# Synology Walthrough

This is a quick walkthrough of setting up the Plex-Meta-Manager Docker container in the Synology UI.

## Prerequisite: Installing Docker

* Open the Package Center app from the Synology Web GUI.

   ![](synology/synology-01.png)

* Type `docker` in the search bar and once it comes up click "Install" to add Docker. and then click "Open" to bring it up.

   ![](synology/synology-02.png)

## Installing Plex Meta Manager

1. Open the Docker app.

   ![](synology/synology-03.png)

2. Search and Download the Image.
   1. Click Registry.
   2. Search for `meisnate12/plex-meta-manager`.
   3. Select the Repository.
   4. Click Download.

   ![](synology/synology-04.png)

3. Select the tag you want to run from the dropdown and click "Select".

   The options are:
    - `latest` - most recent official release; typically the most stable.
    - `develop` - development release, contains new features that haven't made it to latest yet, but may have minor problems.
    - `nightly` - bleeding-edge development version; latest fixes go here, but breakage should be expected.

   ![](synology/synology-05.png)

4. Select the Image and Create a Container.
   1. Click Image.
   2. Select the `meisnate12/plex-meta-manager` Image.
   4. Click Launch.

   ![](synology/synology-06.png)

<br>

**From this point on the setup looks a little different depending on if the Synology is running DiskStation Manager 7 or DiskStation Manager 6.**

````{tab} DiskStation Manager 7

5. Specify your docker network type. Then click "Next".

   ![](synology/dsm7-01.png)

6. You can name the Container whatever you want using the "Container Name" text Box.

   ![](synology/dsm7-02.png)

7. To add Environment Variables and Command Line Arguments click "Advanced Settings". (Optional)

   Information on available Command Line Arguments and Environment Variables can be found [here](../environmental)

   To add an Environment Variable click "Environment" then click Add" and then fill in the Variable and Value.

   ![](synology/dsm7-03.png)

   To use Command Line Arguments click "Execution Command" put the arguments in the "Command" text field.

   ![](synology/dsm7-04.png)

   Click "Save" to save the settings and go back to the General Settings Screen.

8. Click "Next" from the General Settings Screen to get to the Port Settings Screen where you just want to click "Next" as PMM has no Ports.

   ![](synology/dsm7-05.png)

9. Next we need to add you config folder to the container. From the Volume Settings Screen click "Add Folder".

   ![](synology/dsm7-06.png)

9. Select from your Synology File System where you want to store your PMM config files and then enter `/config` as the "Mount path". Then click "Next" to go to the Summary Page.

   ![](synology/dsm7-07.png)

9. From the Summary Page select "Done" to finish and creating the container.

   ![](synology/dsm7-08.png)

````
````{tab} DiskStation Manager 6

5. You can name the Container whatever you want using the "Container Name" text Box. Then click "Advanced Settings".

   ![](synology/dsm6-01.png)

6. Next we need to add you config folder to the container. Select the "Volume" Tab, click "Add Folder", and select from your Synology File System where you want to store your PMM config files.

   ![](synology/dsm6-02.png)

7. Enter `/config` as the "Mount Point".

   ![](synology/dsm6-03.png)

8. Select the "Environment" Tab. (Optional)
   
   Environment Variables and Command Line Arguments can be added here.

   - To add an Environment Variable Click "Add" and then fill in the Variable and Value.
   - To use Command Line Arguments put the arguments in the "Command" text field.

   Information on available Command Line Arguments and Environment Variables can be found [here](../environmental)

   ![](synology/dsm6-04.png)

9. Select "Apply" to save the "Advanced Settings", select "Next" to go to the Summary, and select "Done" to finish and creating the container.

   ![](synology/dsm6-05.png)
   
````
