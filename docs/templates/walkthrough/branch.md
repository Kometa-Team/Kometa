
<!--all-->
### I want to use the NAME branch

<!--all-->

<!--local-->
=== ":fontawesome-brands-linux: Linux"

    [type this into your terminal]
    ```shell { .no-copy }
    cd ~/Kometa
    git checkout BRANCH
    git pull
    source kometa-venv/bin/activate
    python -m pip install -r requirements.txt
    ```

=== ":fontawesome-brands-apple: macOS"

    [type this into your terminal]
    ```shell { .no-copy }
    cd ~/Kometa
    git checkout BRANCH
    git pull
    source kometa-venv/bin/activate
    python -m pip install -r requirements.txt
    ```

=== ":fontawesome-brands-windows: Windows"

    [type this into your terminal]
    ```shell { .no-copy }
    cd ~/Kometa
    git checkout BRANCH
    git pull
    .\kometa-venv\Scripts\activate
    python -m pip install -r requirements.txt
    ```

<!--local-->

<!--docker-->
=== ":fontawesome-brands-docker: docker"

    Add the `BRANCH` tag to the image name in your run command [or wherever you specify the image in your environment]
    
    ```shell { .no-copy }
    docker run --rm -it -v "KOMETA_PATH_GOES_HERE:/config:rw" kometateam/kometa:BRANCH --run
                                                                                ^^^^^^^
    ```
    
    This may not work if you are not using the official image.

<!--docker-->

<!--unraid-->
=== ":fontawesome-brands-linux: unRAID"

    Add the `BRANCH` tag to the image name in your `Repository:` setting for the Kometa unRAID app: [kometateam/kometa:BRANCH]
    
    ```shell { .no-copy }
    kometateam/kometa:BRANCH
                      ^^^^^^^
    ```
    
    Enter that here in the template:

    ![unraid-repo](./../../../../assets/images/kometa/install/unraid-repo.png)

<!--unraid-->

