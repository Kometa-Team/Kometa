<!--all-->
Then run Kometa:

<!--all-->
<!--unraid-->
[type this into your Kometa `>_Console`]
<!--unraid-->

<!--local-docker-->
[type this into your terminal]
<!--local-docker-->

<!--all-->

```shell
<!--all-->
<!--local-unraid-->
python kometa.py -r
<!--local-unraid-->
<!--docker-->
docker run --rm -it -v "KOMETA_PATH_GOES_HERE:/config:rw" kometateam/kometa --run
<!--docker-->
<!--all-->
```
<!--all-->