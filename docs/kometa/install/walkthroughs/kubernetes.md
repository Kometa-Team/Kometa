---
hide:
  - toc
---
# Kubernetes Walkthrough

This article will walk you through getting Kometa set up and running in Kubernetes. It will cover:

1. Creating the Kubernetes CronJob
2. Creating configuration files as Config Maps
3. (Advanced) Creating dynamic configuration files with an Init Container


## Prerequisites.

This walk through assumes you are familiar with Kubernetes concepts and have an exiting cluster to deploy into. 
If you do not, but are interested, [minikube](https://minikube.sigs.k8s.io/docs/start/) is a great place to start.

## Creating the Kubernetes CronJob

When running Kometa in Kubernetes, executing it as a CronJob gives us the ability to define a schedule for execution and have Kubernetes manage the rest.

Some parts of this to tweak to your needs:

1. The namespace should be set to whatever you desire, in this example it runs in the `media` namespace.
2. The schedule, in this example it runs at 00:00 UTC. [https://crontab.guru/](https://crontab.guru/) is a good site if you aren't sure on how to create a schedule.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: kometa
  namespace: media
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          securityContext:
            runAsUser: 1000
            runAsGroup: 1000
          containers:
            - name: kometa
              image: kometateam/kometa:latest
              imagePullPolicy: IfNotPresent
              args: [ "--run", "--read-only-config" ]
              resources:
                limits:
                  cpu: 100m
                  memory: 256Mi
                requests:
                  cpu: 100m
                  memory: 125Mi
              volumeMounts:
                - name: config
                  mountPath: /config
                - name: kometa-config
                  mountPath: /config/config.yml
                  subPath: config.yml
                - name: movie-config
                  mountPath: /config/movies.yaml
                  subPath: movies.yaml
                - name: tv-config
                  mountPath: /config/tv.yaml
                  subPath: tv.yaml
          volumes:
            - name: config
              persistentVolumeClaim:
                claimName: kometa
            - configMap:
                name: kometa-config
              name: kometa-config
            - configMap:
                name: movie-config
              name: movie-config
            - configMap:
                name: tv-config
              name: tv-config
          restartPolicy: OnFailure
```

???+ warning

    If you are using [Longhorn](https://longhorn.io/) as your storage class, you should omit the 
    `spec.jobTemplate.spec.template.spec.securityContext` node to fix file permission errors.

This CronJob also requires

1. A Persistent Volume Claim
2. 3 Config Maps (see next section)

The Persistent Volume Claim (PVC) can be as simple as:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  labels:
    app: kometa
  name: kometa
  namespace: media
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 128Mi

```

## Creating the Config Maps

In Kubernetes, configurations are managed via Config Maps. So we deploy the configurations for Kometa as config maps. The
minimum requirement is the Kometa config, but the example here assumes you have a separate config for movies and tv shows.

### Kometa Config

Here's a config map for the `config.yml` file for Kometa. Note there are many placeholders that will need update based on your environment and needs.

Follow the [Trakt Attributes](../../../config/trakt.md) directions for generating the OAuth authorization values.

```yaml
apiVersion: v1
data:
  config.yml: |
    libraries:
      Movies:
        collection_files:
          - file: config/movies.yaml
      TV Shows:
        collection_files:
          - file: config/tv.yaml
    settings:
      cache: true
      cache_expiration: 60
      asset_directory: config/assets
      asset_folders: true
      asset_depth: 0
      create_asset_folders: false
      dimensional_asset_rename: false
      download_url_assets: false
      show_missing_season_assets: false
      sync_mode: append
      minimum_items: 1
      default_collection_order:
      delete_below_minimum: true
      delete_not_scheduled: false
      run_again_delay: 2
      missing_only_released: false
      only_filter_missing: false
      show_unmanaged: true
      show_filtered: false
      show_options: false
      show_missing: true
      show_missing_assets: true
      save_report: true
      tvdb_language: eng
      ignore_ids:
      ignore_imdb_ids:
      playlist_sync_to_users: all
      verify_ssl: true
    plex:
      url: http://PLEX_IP_HERE:32400
      token: YOUR_TOKEN_HERE
      timeout: 60
      db_cache: 
      clean_bundles: false
      empty_trash: false
      optimize: false
    tmdb:
      apikey: YOUR_API_KEY_HERE
      language: en
    tautulli:
      url: http://TAUTULLI_IP_HERE:8182
      apikey: TAUTULLI_API_KEY_HERE
    omdb:
      apikey: OMDB_API_KEY
    radarr:
      url: http://RADARR_IP_HERE:7878
      token: RADARR_TOKEN_HERE
      add_missing: false
      root_folder_path: /movies
      monitor: false
      availability: cinemas
      quality_profile: HD - 720p/1080p
      tag: kometa
      add_existing: false
      search: false
      radarr_path:
      plex_path:
    sonarr:
      url: http://SONARR_IP_HERE:8989
      token: SONARR_TOKEN_HERE
      add_missing: false
      add_existing: false
      root_folder_path: /tv
      monitor: pilot
      quality_profile: HD - 720p/1080p
      language_profile: English
      series_type: standard
      season_folder: true
      tag: kometa
      search: true
      cutoff_search: false
      sonarr_path:
      plex_path:
    trakt:
      client_id: YOUR_CLIENT_ID_HERE
      client_secret: YOUR_CLIENT_SECRET_HERE
      authorization:
          access_token: YOUR_ACCESS_TOKEN_HERE
          token_type: Bearer
          expires_in: 7889237
          refresh_token: YOUR_REFERSH_TOKEN_HERE
          scope: public
          created_at: 1642462048
kind: ConfigMap
metadata:
  name: kometa-config
  namespace: media
```

### Movie Config Map

Config maps for collections (movies in this example) are more simple!

```yaml
apiVersion: v1
data:
  movies.yaml: |
    collections:
      Trakt Popular:
        trakt_popular: 200
        collection_order: custom
        sync_mode: sync
        sort_title: Traktpopular
        summary: The most popular movies for all time.
        radarr_add_missing: true
        radarr_search: true
        radarr_monitor: true
      Tautulli Most Popular Movies:
        sync_mode: sync
        collection_order: custom
        tautulli_watched:
          list_days: 180
          list_size: 10
          list_minimum: 1
kind: ConfigMap
metadata:
  name: movie-config
  namespace: media
```

### TV Config Map

```yaml
apiVersion: v1
data:
  tv.yaml: |
    collections:
      Most Popular:
        smart_label: originally_available.desc
        sync_mode: sync
        imdb_search:
          type: tv_series, tv_mini_series
          limit: 10
        summary: The 10 most popular shows across the internet
        sonarr_add_missing: true
        sonarr_search: true
        sonarr_monitor: pilot
      Tautulli Most Popular:
        sync_mode: sync
        collection_order: custom
        summary: The 10 most popular shows from Plex users
        tautulli_popular:
          list_days: 180
          list_size: 10
kind: ConfigMap
metadata:
  name: tv-config
  namespace: media
```

## Creating dynamic configuration files with an Init Container

IMDb search results may include results for media which has not yet been released, resulting in a collection that is incomplete. 
In order to solve for this you can replace a static config map with a config file that is (re)generated when the cronjob starts each time. 
This can be done by including an init container which renders a [Jinja](https://jinja.palletsprojects.com/en/3.0.x/templates/) template to a file in the PVC.

### Including the Init Container in the Cron Job

NOTE the environment value named `JINJA_DEST_FILE` is the resulting name of the generated config file.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: kometa
  namespace: media
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          securityContext:
            runAsUser: 1000
            runAsGroup: 1000
          initContainers:
            - name: render-dynamic-config
              image: chrisjohnson00/jinja-init:v1.0.0
              env:
                # source and destination files
                - name: JINJA_SRC_FILE
                  value: /config_src/tv.yaml
                - name: JINJA_DEST_FILE
                  value: /config/tv.yaml
                # let's be verbose
                - name: VERBOSE
                  value: "1"
              volumeMounts:
                # configMap mount point
                - name: tv-config-template
                  mountPath: /config_src
                # target directory mount point; the final config file will be created here
                - name: config
                  mountPath: /config
          containers:
            - name: kometa
              image: kometateam/kometa:latest
              imagePullPolicy: Always
              args: [ "--run", "--read-only-config" ]
              resources:
                limits:
                  cpu: 100m
                  memory: 256Mi
                requests:
                  cpu: 100m
                  memory: 125Mi
              volumeMounts:
                - name: config
                  mountPath: /config
                - name: kometa-config
                  mountPath: /config/config.yml
                  subPath: config.yml
                - name: movie-config
                  mountPath: /config/movies.yaml
                  subPath: movies.yaml
          volumes:
            - name: config
              persistentVolumeClaim:
                claimName: kometa
            - configMap:
                name: kometa-config
              name: kometa-config
            - configMap:
                name: movie-config
              name: movie-config
            - configMap:
                name: tv-config-jinja-template
              name: tv-config-template
          restartPolicy: OnFailure
```


### Templatizing your configuration

`{{ now().strftime('%Y-%m-%d') }}` is the Jinja code, which when rendered will be replaced with the current date in YYYY-MM-DD format. 
`now()` is a special method defined in the Python code running in the init container to allow access to the current date, 
so changing the output format is as simple as changing the string in `strftime` to your desired date/time format for your list source.

```yaml
apiVersion: v1
data:
  tv.yaml: |
    collections:
      Most Popular:
        smart_label: originally_available.desc
        sync_mode: sync
        imdb_search:
          type: tv_series, tv_mini_series
          release.after: 1979-12-31
          release.before: {{ now().strftime('%Y-%m-%d') }}
          limit: 10
        summary: The 10 most popular shows across the internet
        sonarr_add_missing: true
        sonarr_search: true
        sonarr_monitor: pilot
      Tautulli Most Popular:
        sync_mode: sync
        collection_order: custom
        summary: The 10 most popular shows from Plex users
        tautulli_popular:
          list_days: 180
          list_size: 10
kind: ConfigMap
metadata:
  name: tv-config-jinja-template
  namespace: media
```
