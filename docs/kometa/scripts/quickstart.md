---
hide:
  - toc
---
???+ danger
    
    **Quickstart is in early development.** Please provide feedback via the 
    [quickstart-feedback Discord channel](https://discord.com/channels/822460010649878528/1335372922306695198)

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="<!--logo-start-->"
  end="<!--logo-end-->"
  rewrite-relative-urls=false
%}

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="<!--body1-start-->"
  end="<!--body1-end-->"
  rewrite-relative-urls=false
%}

???+ danger

    **We strongly recommend running this yourself rather than relying on someone else to host Quickstart.**

    This ensures that connection attempts are made exclusively to services and machines accessible only to you. Additionally, all credentials are stored locally, safeguarding your sensitive information from being stored on someone else's machine.

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="<!--body2-start-->"
  end="<!--body2-end-->"
  rewrite-relative-urls=false
%}

???+ tip

    You will likely need to perform these steps first to have a system tray icon show up:

    ```shell
    sudo apt update
    sudo apt install -y libxcb-xinerama0 libxcb-xinerama0-dev libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0
    ```

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="<!--body3-start-->"
  end="<!--body3-end-->"
  rewrite-relative-urls=false
%}