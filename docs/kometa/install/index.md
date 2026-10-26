# Install Kometa

Choose where you will run Kometa to see a complete installation walkthrough. You will install Kometa, connect it to Plex and TMDb, and verify your first run. Sample collections and overlays are optional next steps.

Kometa uses YAML configuration and has no graphical interface. You can run it on a different machine from Plex. Docker is recommended when you do not already have a reason to use local Python, because its image supplies Python and dependencies.

<form id="install-questionnaire" hidden aria-label="Choose your installation environment">
  <label for="install-env">Where will Kometa run?</label>
  <select id="install-env" name="env">
    <option value="">Choose an environment</option>
    <option value="windows">Windows</option><option value="macos">macOS</option><option value="linux">Linux</option>
    <option value="unraid">unRAID</option><option value="qnap">QNAP</option><option value="synology">Synology</option><option value="truenas">TrueNAS</option><option value="kubernetes">Kubernetes</option>
  </select>
  <div id="install-method-field" hidden><label for="install-method">How do you want to install Kometa?</label>
    <select id="install-method" name="method"><option value="">Choose an installation method</option><option value="docker">Docker (recommended)</option><option value="local">Local Python</option></select>
  </div>
  <div id="install-launch-field" hidden><label for="install-launch">How will you manage Docker?</label>
    <select id="install-launch" name="launch"><option value="">Choose a Docker method</option><option value="run">Docker Run</option><option value="compose">Docker Compose</option></select>
  </div>
  <div id="install-version-field" hidden><label for="install-version">Which platform version?</label>
    <select id="install-version" name="version"><option value="">Choose a version</option><option value="current">Current documented version</option><option value="legacy">Older version</option></select>
  </div>
  <button type="button" id="install-reset">Reset choices</button>
  <p id="install-summary" role="status" aria-live="polite"></p>
</form>

<div id="install-fallback" markdown="1">

## Installation paths

JavaScript enables the questionnaire. You can also browse all paths below:

- [Local Python](#path-local)
- [Docker Run](#path-docker)
- [Docker Compose](#path-compose)
- [unRAID](#path-unraid)
- [QNAP](#path-qnap)
- [Synology](#path-synology)
- [TrueNAS](#path-truenas)
- [Kubernetes](#path-kubernetes)
- [Configuration and first run](#configuration)

</div>

<div id="install-instructions" markdown="1">

<section class="install-path" data-method="local" markdown="1">

## Local Python {#path-local}

{% include-markdown "../../templates/install/local.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-method="docker" data-launch="run" markdown="1">

## Docker run {#path-docker}

{% include-markdown "../../templates/install/docker.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-env="unraid" markdown="1">

## unRAID {#path-unraid}

{% include-markdown "../../templates/install/unraid.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-env="kubernetes" markdown="1">

## Kubernetes {#path-kubernetes}

{% include-markdown "../../templates/install/kubernetes.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-env="qnap" markdown="1">

## QNAP {#path-qnap}

{% include-markdown "../../templates/install/qnap.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-env="synology" markdown="1">

## Synology {#path-synology}

{% include-markdown "../../templates/install/synology.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-env="truenas" markdown="1">

## TrueNAS {#path-truenas}

{% include-markdown "../../templates/install/truenas.md" rewrite-relative-urls=false %}

</section>

<section class="install-path" data-method="docker" data-launch="compose" markdown="1">

## Docker Compose {#path-compose}

{% include-markdown "../../templates/install/compose.md" rewrite-relative-urls=false %}

</section>

{% include-markdown "../../templates/install/configuration.md" rewrite-relative-urls=false %}

</div>
