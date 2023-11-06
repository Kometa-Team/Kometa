=== ":fontawesome-brands-linux: Linux"

    [type this into your terminal]
    
    ```
    nano config/config.yml
    ```
    
    I’m using `nano` here mostly because it’s simpler than any other editor on Linux.
    
    If you see something like:
    ```bash
     $ nano config/config.yml
    zsh: command not found: nano
    ```
    
    You need to install `nano`, which you would do with:
    
    [type this into your terminal]
    
    ```
    sudo apt install nano
    ```
    
    You can use any other text editor you wish, provided it saves files as PLAIN TEXT.  `vi`, `emacs`, etc.

=== ":fontawesome-brands-apple: macOS"

    [type this into your terminal]
    
    ```
    nano config/config.yml
    ```
    
    I’m using `nano` here simply because it’s built into OSX.  You can use any other text editor you wish, provided it saves files as PLAIN TEXT.  BBedit, TextMate, VSCode, etc.
    
    A common mistake is using TextEdit.app, which saves files as RTF by default.

=== ":fontawesome-brands-windows: Windows"

    [type this into your terminal]

    ```
    notepad .\config\config.yml
    ```
    I’m using `notepad` here simply because it’s built into Windows.  You can use any other text editor you wish, provided it saves files as PLAIN TEXT.
    


From here on in, when this walkthrough says "open the config file", I mean this `nano` or `notepad` command.  **Don't copy the template again**.
