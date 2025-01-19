# CLIntercept

A simple lightweight tool to intercept incoming and outgoing HTTP packets using HTTP proxy to view, modify and edit them. It's extremely useful for quick tests and modifications on HTTP packets without needing to load heavy tools like Burp or ZAP. If you want to read more about forward proxies, check out my [blog post](https://ch1y0w0.github.io/2024/12/16/How-Forward-Proxies-Work.html)

# Why?

Well, it's not optimal for complex works but it's extremely useful for quick modification needs for example when you're exploring a webpage and you get curious if it's vulnerable to a bug. You can run CLIntercept using a simple command instead of waiting for Burp Suite to load. Or when you need to debug something really quick. Anyway, here are some advantages of CLIntercept over other tools:
1. Simple and begginer-friendly
2. Fast
3. Lightweight
4. Written in raw Python with as less as dependencies possible

# No I Mean Seriously, WHY?

Well, i had times when i needed to do a quick debugging on packets but due to lack of this tool, i had to wait minutes for Burp to load and also deal with its interface. So i decided to write this tool that only needs a single command to run and do the main things that Burp is created for. Also i'm addicted to coding... so yeah.

# Installation

You don't need any complex installation process. Just clone the repository and run the script

`git clone https://github.com/ch1y0w0/CLIntercept.git`

# Usage

I tried to make it as simple as possible. For help, use `-h` flag.

```
usage: proxy.py [-h] [-target TARGET] [-ip IP] [-port PORT]

Packet interceptor and controller.

options:
  -h, --help      show this help message and exit
  -target TARGET  Specify the target IP to filter packets.
  -ip IP          Specify the listening IP address.
  -port PORT      Specify the listening port.
```

To run the proxy server:
```
python proxy.py
```

Setting a target will only print the packets belong to the target and will automatically forward any other packet:
```
python proxy.py -target google
```

You can now set `127.0.0.1:8080` as your proxy server.

# Disclaimer

This tool is still in development phase and lacks many useful features. I'm actively developing it for my personal use so make sure to watch for changes. Any contribution is appreciated. And you can always reach to me at my [X](https://x.com/Ch1y0w0)

*Note: (HTTPS support is in progress)*

# ToDo List
	[X] ~~Fix Forwarding Back to Browser~~
	[X] ~~Not Working On All Hosts~~
	[ ] Modify Packets
	[ ] HTTPS (Certificate generation)
	[X] ~~Full Rework~~