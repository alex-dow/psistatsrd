Psistats Rearview Display (PsistatsRD) v0.0.1
=============================================

Version 0.0.1
-------------

An application to display graphs and other information from Psistats
information on small screens.

This application is designed to on small resolution screens. It's name
comes from the first usage of the application, a display on a $20 320x280
screen used for rearview cameras in cars.

How it Works
------------

PsistatsRD creates a queue on the RabbitMQ server. It then gets a list
of queues that the configured user has access to. If the queue has the
prefix "psistats-", then PsistatsRD will bind the queue it created to the
queue it found.

Every second, PsistatsRD will consume all available messages on its own
queue, and with that information create a display.

Data Structure
--------------

The messages should be utf-8 encoded json with the following structure:

```javascript
{
    "cpu": 0.0,    // CPU usage percent, float from 0 to 100
    "mem_used": 0, // Memory used, integer bytes
    "mem_free": 0, // Availalbe memory, integer bytes
    "mem_total": 0, // Total memory, integer bytes
    "ipaddr": "127.0.0.1", // IP Address. String or array of multiple
                           // ips.
    "hostname": "compname" // Hostname or computer name
    "uptime": "12d:12h:32m:12s" // Uptime
}
```








--
