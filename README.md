# govee-lan-server-py
Simple Python API server for controlling Govee lights via their LAN API

This is a very crude API. I'm mainly using it to turn a light strip on and off.

I first wrote this as [govee-lan-server](https://github.com/20goto10/govee-lan-server) in Node.js but I ran into some problems with the library under the hood. I figured I could write this quicker than I could debug that library (and I did). This README is mostly copied from the Node original.

# What it does
Govee-lan-server is a lightweight web server that can handle a few simple actions for controlling one or more Govee lights. This uses their new local LAN API, via RhinoMcd's [govee-lan-api](https://github.com/Rhinomcd/govee-lan-api) Python library. It does NOT use Govee's remote API or BLE; it must run within the device's LAN.

I wanted an always-on event listener to reduce latency caused by the startup "discovery" phase. (The Node version does that successfully; the Python version rediscovers on every request, for the time being, but the latency is not bad.)

Using a web server is the easiest way to make it reachable from the separate system that will be controlling it (a rooted Philips Hue hub). I use a Philips Hue dimmer switch control my Govee lights, using a Python script I wrote that runs on a rooted Hue: [hue-jazz](https://github.com/20goto10/hue-jazz/). You could also issue the same requests from other home automation software. 

I will likely abandon this project as soon as there is a good OpenHAB binding for these kinds of light strips.

# Improvements
A couple small details differ from the Node version. There's no "fade" option (which wasn't all that great anyway). The device map in the config is no longer mandatory (and the nicknames are in more logical nickname->ID order).

# Warning!
Don't run this on a publicly accessible server, unless you know what you're doing. There's no access control, and I don't want to be responsible for any involuntary lightshows. The risk of a serious hack is pretty small but I'd rather not be responsible for any part of it.

# How to do it

0. Prereqs-- you need Python 3.10 or higher, the Flask library (simple HTTP server) and govee-lan-api (which is doing the work here)
```
git clone https://github.com/20goto10/govee-lan-server-py
cd govee-lan-server-py
pip install flask
pip install govee-lan-api
cp config.json.sample config.json
```

1. Make sure you have the Govee "LAN Control" option in Govee's confusing app. This is not a straightforward matter. I had to try several things to wake this up. I'm not sure what eventually got it to work, but it might be the tip I found on Reddit to link the device to your phone's wi-fi hotspot. I also deleted and reset the device, power-cycled it numerous times, and restarted the app numerous times. All I can say for sure is that I have an H61E1 and it did eventually work. Why the LAN Control option is not visibile by default, or easy to enable, is anyone's guess. If you unplug it and plug it back in 30 minutes later as the Govee docs suggest, you have probably just wasted 30 minutes.


2. Edit `config.json` and map nicknames to device IDs for whichever devices you wish to use, by ID. If you're not sure of the device ID, change DEBUG_MODE to True and launch the server (per the next step). When the server discovers a device, it will print out the ID. Use that as the device query parameter, or set a key by nickname with the ID as the value in the 'device_map' section of the JSON config.

   The rest of the config, currently, is just a port setting for your server (default should be fine).


3. Start the app.
```
python govee-lan-server.py
````

4. Once the app is running, you can trigger the HTTP requests however you like (e.g. from curl, or a browser). See below for examples.

5. (optional) A systemd service daemon script is included in the `service` directory. It must be updated and copied to the correct location. See README in that directory.


## Using the API

Note that if running these curl commands in a terminal you will need to escape the & characters (i.e. change them to "\\&").

To run them via a browser you can just omit the word "curl". (Well, if you made it this far, you probably know that, but anyway...) The server doesn't care what HTTP request method you use.

Supposing it's running at 192.168.1.230, on the default port of 3666, and your device nickname in the device_map is "lightstrip". Note you can also use the actual ID.

To turn it on:

`curl http://192.168.1.230:3666?device=lightstrip&action=on`

To turn it off:

`curl http://192.168.1.230:3666?device=lightstrip&action=off`

Set the brightness (in this case to 50%). The brightness scale is 0-100.

`curl http://192.168.1.230:3666?device=lightstrip&action=brightness&value=50`

Set the color, in this case, to 100% green-ness. 

`curl http://192.168.1.230:3666?device=lightstrip&action=color&value=00FF00`


That's pretty much it.  Valid actions are:
```
on
off
color
brightness
```


# Contributing
Please, feel free. My apologies for the sloppy code and Python offenses. This is something I hacked together in a couple hours in vi on a Raspberry pi.

# Ranting
All IoT devices should have a local API. The trend of having them handling their most basic jobs over the internet, instead of strictly within the LAN, has always struck me as insane. 

