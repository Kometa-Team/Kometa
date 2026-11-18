---
hide:
  - toc
---
???+ danger

    **This script is destructive with NO UNDO.**

    This script is intended as a last resort to repair a damaged Kometa installation.

{%    
  include-markdown "https://raw.githubusercontent.com/Kometa-Team/Overlay-Reset/develop/README.md"
  comments=false
  replace='{
    "### Install Walkthroughs": "### Install walkthroughs",
    "### Local Install Overview": "### Local install overview",
    "### Docker Install Overview": "### Docker install overview",
    "#### Docker Run:": "#### Docker run:",
    "### Example .env File": "### Example .env file"
}'
%}
