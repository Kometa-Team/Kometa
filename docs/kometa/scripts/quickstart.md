# Quickstart

Quickstart helps you configure Kometa through a guided web interface. It is a separate project with its own installation and updates.

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="<!--logo-start-->"
  end="<!--logo-end-->"
  replace='{
    "(docs/plex-security.md)": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/plex-security.md)",
    "(#-features)": "(#features)",
    "(#config-management--history)": "(#config-management-history)",
    "(#live-previews--assets)": "(#live-previews-assets)",
    "(#themes--personalization)": "(#themes-personalization)",
    "(#logscan-analyzer--analytics-page)": "(#logscan-analyzer-analytics-page)",
    "(#support--troubleshooting)": "(#support-troubleshooting)",
    "(#data--privacy-quickstart)": "(#data-privacy-quickstart)",
    "(#1---installing-on-windows)": "(#1-installing-on-windows)",
    "(#2---installing-on-mac)": "(#2-installing-on-mac)",
    "(#3---installing-on-ubuntu-linux)": "(#3-installing-on-ubuntu-linux)",
    "(#4---running-in-docker)": "(#4-running-in-docker)",
    "(#5---installing-locally)": "(#5-installing-locally)",
    "(#debugging--changing-ports)": "(#debugging-changing-ports)",
    "(static/": "(https://raw.githubusercontent.com/Kometa-Team/Quickstart/develop/static/",
    "(docs/": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/",
    "\n  - ": "\n    - ",
    "## Welcome to Kometa Quickstart": "",
    "### Multiple Ways to Run Quickstart": "### Multiple ways to run Quickstart",
    "### Safe Playground Mode": "### Safe playground mode",
    "### Config Management & History": "### Config management & history",
    "### Config Bundles": "### Config bundles",
    "### Guided, Validated Workflow": "### Guided, validated workflow",
    "### Kometa Gates": "### Kometa gates",
    "### Kometa Runtime Modes": "### Kometa runtime modes",
    "### Built-in App Runners": "### Built-in app runners",
    "#### Optional Integrations": "#### Optional integrations",
    "### Live Previews & Assets": "### Live previews & assets",
    "### Automatic Updates": "### Automatic updates",
    "### Themes & Personalization": "### Themes & personalization",
    "#### Startup Analytics Migrations": "#### Startup analytics migrations",
    "### Logscan Analyzer & Analytics Page": "### Logscan analyzer & analytics page",
    "### Import Existing Config": "### Import existing config",
    "### Quickstart Scope": "### Quickstart scope",
    "### Support & Troubleshooting": "### Support & troubleshooting",
    "### Data & Privacy (Quickstart)": "### Data & privacy (Quickstart)",
    "### Development Transparency": "### Development transparency",
    "## Table of Contents": "## Table of contents",
    "### Missing stdlib C extensions (sqlite3, _ssl, etc.)": "### Missing stdlib c extensions (sqlite3, _ssl, etc.)",
    "### Debugging & Changing Ports": "### Debugging & changing ports",
    "### Developer Testing": "### Developer testing",
    "## Frontend Tooling": "## Frontend tooling",
    "### Which files Vite knows about": "### Which files vite knows about",
    "## Appendix: Dependency Map": "## Appendix: dependency map"
}'
  rewrite-relative-urls=false
%}

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="<!--body1-start-->"
  end="## Table of Contents"
  replace='{
    "(docs/plex-security.md)": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/plex-security.md)",
    "(#-features)": "(#features)",
    "(#config-management--history)": "(#config-management-history)",
    "(#live-previews--assets)": "(#live-previews-assets)",
    "(#themes--personalization)": "(#themes-personalization)",
    "(#logscan-analyzer--analytics-page)": "(#logscan-analyzer-analytics-page)",
    "(#support--troubleshooting)": "(#support-troubleshooting)",
    "(#data--privacy-quickstart)": "(#data-privacy-quickstart)",
    "(#1---installing-on-windows)": "(#1-installing-on-windows)",
    "(#2---installing-on-mac)": "(#2-installing-on-mac)",
    "(#3---installing-on-ubuntu-linux)": "(#3-installing-on-ubuntu-linux)",
    "(#4---running-in-docker)": "(#4-running-in-docker)",
    "(#5---installing-locally)": "(#5-installing-locally)",
    "(#debugging--changing-ports)": "(#debugging-changing-ports)",
    "(static/": "(https://raw.githubusercontent.com/Kometa-Team/Quickstart/develop/static/",
    "(docs/": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/",
    "\n  - ": "\n    - ",
    "## Welcome to Kometa Quickstart": "",
    "### Multiple Ways to Run Quickstart": "### Multiple ways to run Quickstart",
    "### Safe Playground Mode": "### Safe playground mode",
    "### Config Management & History": "### Config management & history",
    "### Config Bundles": "### Config bundles",
    "### Guided, Validated Workflow": "### Guided, validated workflow",
    "### Kometa Gates": "### Kometa gates",
    "### Kometa Runtime Modes": "### Kometa runtime modes",
    "### Built-in App Runners": "### Built-in app runners",
    "#### Optional Integrations": "#### Optional integrations",
    "### Live Previews & Assets": "### Live previews & assets",
    "### Automatic Updates": "### Automatic updates",
    "### Themes & Personalization": "### Themes & personalization",
    "#### Startup Analytics Migrations": "#### Startup analytics migrations",
    "### Logscan Analyzer & Analytics Page": "### Logscan analyzer & analytics page",
    "### Import Existing Config": "### Import existing config",
    "### Quickstart Scope": "### Quickstart scope",
    "### Support & Troubleshooting": "### Support & troubleshooting",
    "### Data & Privacy (Quickstart)": "### Data & privacy (Quickstart)",
    "### Development Transparency": "### Development transparency",
    "## Table of Contents": "## Table of contents",
    "### Missing stdlib C extensions (sqlite3, _ssl, etc.)": "### Missing stdlib c extensions (sqlite3, _ssl, etc.)",
    "### Debugging & Changing Ports": "### Debugging & changing ports",
    "### Developer Testing": "### Developer testing",
    "## Frontend Tooling": "## Frontend tooling",
    "### Which files Vite knows about": "### Which files vite knows about",
    "## Appendix: Dependency Map": "## Appendix: dependency map"
}'
  rewrite-relative-urls=false
%}

## Prerequisites

{%
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Quickstart/refs/heads/develop/README.md"
  comments=false
  start="## Prerequisites"
  end="<!--body1-end-->"
  replace='{
    "(docs/plex-security.md)": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/plex-security.md)",
    "(#-features)": "(#features)",
    "(#config-management--history)": "(#config-management-history)",
    "(#live-previews--assets)": "(#live-previews-assets)",
    "(#themes--personalization)": "(#themes-personalization)",
    "(#logscan-analyzer--analytics-page)": "(#logscan-analyzer-analytics-page)",
    "(#support--troubleshooting)": "(#support-troubleshooting)",
    "(#data--privacy-quickstart)": "(#data-privacy-quickstart)",
    "(#1---installing-on-windows)": "(#1-installing-on-windows)",
    "(#2---installing-on-mac)": "(#2-installing-on-mac)",
    "(#3---installing-on-ubuntu-linux)": "(#3-installing-on-ubuntu-linux)",
    "(#4---running-in-docker)": "(#4-running-in-docker)",
    "(#5---installing-locally)": "(#5-installing-locally)",
    "(#debugging--changing-ports)": "(#debugging-changing-ports)",
    "(static/": "(https://raw.githubusercontent.com/Kometa-Team/Quickstart/develop/static/",
    "(docs/": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/",
    "\n  - ": "\n    - ",
    "## Welcome to Kometa Quickstart": "",
    "### Multiple Ways to Run Quickstart": "### Multiple ways to run Quickstart",
    "### Safe Playground Mode": "### Safe playground mode",
    "### Config Management & History": "### Config management & history",
    "### Config Bundles": "### Config bundles",
    "### Guided, Validated Workflow": "### Guided, validated workflow",
    "### Kometa Gates": "### Kometa gates",
    "### Kometa Runtime Modes": "### Kometa runtime modes",
    "### Built-in App Runners": "### Built-in app runners",
    "#### Optional Integrations": "#### Optional integrations",
    "### Live Previews & Assets": "### Live previews & assets",
    "### Automatic Updates": "### Automatic updates",
    "### Themes & Personalization": "### Themes & personalization",
    "#### Startup Analytics Migrations": "#### Startup analytics migrations",
    "### Logscan Analyzer & Analytics Page": "### Logscan analyzer & analytics page",
    "### Import Existing Config": "### Import existing config",
    "### Quickstart Scope": "### Quickstart scope",
    "### Support & Troubleshooting": "### Support & troubleshooting",
    "### Data & Privacy (Quickstart)": "### Data & privacy (Quickstart)",
    "### Development Transparency": "### Development transparency",
    "## Table of Contents": "## Table of contents",
    "### Missing stdlib C extensions (sqlite3, _ssl, etc.)": "### Missing stdlib c extensions (sqlite3, _ssl, etc.)",
    "### Debugging & Changing Ports": "### Debugging & changing ports",
    "### Developer Testing": "### Developer testing",
    "## Frontend Tooling": "## Frontend tooling",
    "### Which files Vite knows about": "### Which files vite knows about",
    "## Appendix: Dependency Map": "## Appendix: dependency map"
}'
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
  replace='{
    "(docs/plex-security.md)": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/plex-security.md)",
    "(#-features)": "(#features)",
    "(#config-management--history)": "(#config-management-history)",
    "(#live-previews--assets)": "(#live-previews-assets)",
    "(#themes--personalization)": "(#themes-personalization)",
    "(#logscan-analyzer--analytics-page)": "(#logscan-analyzer-analytics-page)",
    "(#support--troubleshooting)": "(#support-troubleshooting)",
    "(#data--privacy-quickstart)": "(#data-privacy-quickstart)",
    "(#1---installing-on-windows)": "(#1-installing-on-windows)",
    "(#2---installing-on-mac)": "(#2-installing-on-mac)",
    "(#3---installing-on-ubuntu-linux)": "(#3-installing-on-ubuntu-linux)",
    "(#4---running-in-docker)": "(#4-running-in-docker)",
    "(#5---installing-locally)": "(#5-installing-locally)",
    "(#debugging--changing-ports)": "(#debugging-changing-ports)",
    "(static/": "(https://raw.githubusercontent.com/Kometa-Team/Quickstart/develop/static/",
    "(docs/": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/",
    "\n  - ": "\n    - ",
    "## Welcome to Kometa Quickstart": "",
    "### Multiple Ways to Run Quickstart": "### Multiple ways to run Quickstart",
    "### Safe Playground Mode": "### Safe playground mode",
    "### Config Management & History": "### Config management & history",
    "### Config Bundles": "### Config bundles",
    "### Guided, Validated Workflow": "### Guided, validated workflow",
    "### Kometa Gates": "### Kometa gates",
    "### Kometa Runtime Modes": "### Kometa runtime modes",
    "### Built-in App Runners": "### Built-in app runners",
    "#### Optional Integrations": "#### Optional integrations",
    "### Live Previews & Assets": "### Live previews & assets",
    "### Automatic Updates": "### Automatic updates",
    "### Themes & Personalization": "### Themes & personalization",
    "#### Startup Analytics Migrations": "#### Startup analytics migrations",
    "### Logscan Analyzer & Analytics Page": "### Logscan analyzer & analytics page",
    "### Import Existing Config": "### Import existing config",
    "### Quickstart Scope": "### Quickstart scope",
    "### Support & Troubleshooting": "### Support & troubleshooting",
    "### Data & Privacy (Quickstart)": "### Data & privacy (Quickstart)",
    "### Development Transparency": "### Development transparency",
    "## Table of Contents": "## Table of contents",
    "### Missing stdlib C extensions (sqlite3, _ssl, etc.)": "### Missing stdlib c extensions (sqlite3, _ssl, etc.)",
    "### Debugging & Changing Ports": "### Debugging & changing ports",
    "### Developer Testing": "### Developer testing",
    "## Frontend Tooling": "## Frontend tooling",
    "### Which files Vite knows about": "### Which files vite knows about",
    "## Appendix: Dependency Map": "## Appendix: dependency map"
}'
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
  replace='{
    "(docs/plex-security.md)": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/plex-security.md)",
    "(#-features)": "(#features)",
    "(#config-management--history)": "(#config-management-history)",
    "(#live-previews--assets)": "(#live-previews-assets)",
    "(#themes--personalization)": "(#themes-personalization)",
    "(#logscan-analyzer--analytics-page)": "(#logscan-analyzer-analytics-page)",
    "(#support--troubleshooting)": "(#support-troubleshooting)",
    "(#data--privacy-quickstart)": "(#data-privacy-quickstart)",
    "(#1---installing-on-windows)": "(#1-installing-on-windows)",
    "(#2---installing-on-mac)": "(#2-installing-on-mac)",
    "(#3---installing-on-ubuntu-linux)": "(#3-installing-on-ubuntu-linux)",
    "(#4---running-in-docker)": "(#4-running-in-docker)",
    "(#5---installing-locally)": "(#5-installing-locally)",
    "(#debugging--changing-ports)": "(#debugging-changing-ports)",
    "(static/": "(https://raw.githubusercontent.com/Kometa-Team/Quickstart/develop/static/",
    "(docs/": "(https://github.com/Kometa-Team/Quickstart/blob/develop/docs/",
    "\n  - ": "\n    - ",
    "## Welcome to Kometa Quickstart": "",
    "### Multiple Ways to Run Quickstart": "### Multiple ways to run Quickstart",
    "### Safe Playground Mode": "### Safe playground mode",
    "### Config Management & History": "### Config management & history",
    "### Config Bundles": "### Config bundles",
    "### Guided, Validated Workflow": "### Guided, validated workflow",
    "### Kometa Gates": "### Kometa gates",
    "### Kometa Runtime Modes": "### Kometa runtime modes",
    "### Built-in App Runners": "### Built-in app runners",
    "#### Optional Integrations": "#### Optional integrations",
    "### Live Previews & Assets": "### Live previews & assets",
    "### Automatic Updates": "### Automatic updates",
    "### Themes & Personalization": "### Themes & personalization",
    "#### Startup Analytics Migrations": "#### Startup analytics migrations",
    "### Logscan Analyzer & Analytics Page": "### Logscan analyzer & analytics page",
    "### Import Existing Config": "### Import existing config",
    "### Quickstart Scope": "### Quickstart scope",
    "### Support & Troubleshooting": "### Support & troubleshooting",
    "### Data & Privacy (Quickstart)": "### Data & privacy (Quickstart)",
    "### Development Transparency": "### Development transparency",
    "## Table of Contents": "## Table of contents",
    "### Missing stdlib C extensions (sqlite3, _ssl, etc.)": "### Missing stdlib c extensions (sqlite3, _ssl, etc.)",
    "### Debugging & Changing Ports": "### Debugging & changing ports",
    "### Developer Testing": "### Developer testing",
    "## Frontend Tooling": "## Frontend tooling",
    "### Which files Vite knows about": "### Which files vite knows about",
    "## Appendix: Dependency Map": "## Appendix: dependency map"
}'
  rewrite-relative-urls=false
%}
