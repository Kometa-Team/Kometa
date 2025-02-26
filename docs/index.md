<style>
.md-content h1, .md-content__button {
    display: none;
}
</style>

<center>
![Logo](assets/images/icons/logo-full.png)

{%
    include-markdown "../README.md"
    start="<!--shield-start-->"
    end="<!--shield-end-->"
%}
</center>

{%
    include-markdown "../README.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}

<div class="grid cards" markdown>

-   :octicons-versions-24:{ .lg .middle } __Overhaul Your Media Libraries__

    ---

    {%
        include-markdown "../README.md"
        start="<!--card1-start-->"
        end="<!--card1-end-->"
    %}
 
-   :octicons-sliders-16:{ .lg .middle } __Kometa Defaults__

    ---

    {%
        include-markdown "../README.md"
        start="<!--card2-start-->"
        end="<!--card2-end-->"
    %}

-   :material-connection:{ .lg .middle } __Third-Party Integrations__

    ---

    {%
        include-markdown "../README.md"
        start="<!--card3-start-->"
        end="<!--card3-end-->"
    %}

    {%
        include-markdown "../README.md"
        start="<!--card4-start-->"
        end="<!--card4-end-->"
    %}

-   :material-tools:{ .lg .middle } __Library Operations__

    ---

    {%
        include-markdown "../README.md"
        start="<!--card5-start-->"
        end="<!--card5-end-->"
    %}

    {%
        include-markdown "../README.md"
        start="<!--card6-start-->"
        end="<!--card6-end-->"
    %}


-   :material-star-face:{ .lg .middle } __And More!__

    ---

    {%
        include-markdown "../README.md"
        start="<!--card7-start-->"
        end="<!--card7-end-->"
    %}

    {%
        include-markdown "../README.md"
        start="<!--card8-start-->"
        end="<!--card8-end-->"
    %}

</div>

{%
    include-markdown "../README.md"
    start="<!--started-start-->"
    end="<!--started-end-->"
    replace='{
        "<img src=\"https://kometa.wiki/en/latest/assets/images/movie-collections.png\" width=\"600\" alt=\"Movie Collection Preview\">": 
        "![Movie Collection Preview](assets/images/movie-collections.png){ width=\"600\" }",
        "<img src=\"https://kometa.wiki/en/latest/assets/images/show-overlays.png\" width=\"600\" alt=\"Show Collection Preview\">": 
        "![Show Collection Preview](assets/images/show-overlays.png){ width=\"600\" }",
        "(https://kometa.wiki/en/latest/": "(", "/)": ".md)"
    }'
    rewrite-relative-urls=false
%}

#### Running in Docker

??? "Develop Branch (click to expand)"

    {%
        include-markdown "../README.md"
        start="<!--develop-start-->"
        end="<!--develop-end-->"
    %}

    === "Running in Docker"
        {%
            include-markdown "../README.md"
            start="<!--develop-docker-start-->"
            end="<!--develop-docker-end-->"
        %}
    === "Running on the Host"
        {%
            include-markdown "../README.md"
            start="<!--develop-host-start-->"
            end="<!--develop-host-end-->"
        %}
    
    {%
        include-markdown "../README.md"
        start="<!--develop2-start-->"
        end="<!--develop2-end-->"
    %}

??? warning "Nightly Branch (click to expand)"

    {%
        include-markdown "../README.md"
        start="<!--nightly-start-->"
        end="<!--nightly-end-->"
    %}

    === "Running in Docker"
        {%
            include-markdown "../README.md"
            start="<!--nightly-docker-start-->"
            end="<!--nightly-docker-end-->"
        %}
    === "Running on the Host"
        {%
            include-markdown "../README.md"
            start="<!--nightly-host-start-->"
            end="<!--nightly-host-end-->"
        %}
    
    {%
        include-markdown "../README.md"
        start="<!--nightly2-start-->"
        end="<!--nightly2-end-->"
    %}

{%
    include-markdown "../README.md"
    start="<!--outro-start-->"
    end="<!--outro-end-->"
%}