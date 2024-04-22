The commands you've been using in this walkthrough run Kometa immediately then quit.

Kometa also features multiple layers of scheduling, which you can leverage to control when various activities take place.

 - You can run Kometa in the background, telling it to wake up and process your libraries at fixed times during the day.  The default behavior in this regard is to wake up at 5AM and process the config.  If you leave the `-r` off the commands you have been using in this walkthrough, that's what will happen.

   You can control when Kometa wakes up with the [time-to-run](../../environmental.md) env-var/runtime flag.

 - You can skip using that internal schedule and just do manual runs as you have been doing throughout this walkthrough using standard tools available in your OS.

   Details on setting this up are found [here](../../guides/scheduling.md).

 - In addition, individual items *within* the configuration can be scheduled to take place at certain times *provided Kometa is running at that time*.  For example, you can tell Kometa only to apply overlays on Tuesdays or the like.  You can then schedule manual runs every day at noon and overlays will only get processed when it runs on Tuesday.  This sort of schedule *will not* make Kometa start up if it is not already running.  If you don't arrange for Kometa to be run on Tuesday, your overlays would never be processed in this example.

   Details on this level of scheduling are found [here](../../../config/schedule.md)
