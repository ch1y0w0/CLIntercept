# CLIntercept

A simple lightweight tool to intercept incoming and outgoing HTTP packets using HTTP proxy to view, modify and edit them. It's extremely useful for quick tests and modifications on HTTP packets without needing to load heavy tools like Burp or ZAP. 

# Why?

Well, it's not optimal for complex works but it's extremely useful for quick modification needs for example when you're exploring a webpage and you get curious if it's vulnerable to a bug. You can run CLIntercept using a simple command instead of waiting for Burp Suite to load. Or when you need to debug something really quick. Anyway, here are some advantages of CLIntercept over other tools:
1. Simple and begginer-friendly
2. Fast
3. Lightweight
4. Written in raw Python with as less as dependencies possible

# No I mean Seriously, WHY?

Well, i had times when i needed to do a quick debugging on packets but due to lack of this tool, i had to wait minutes for Burp to load and also deal with its interface. So i decided to write this tool that only needs a single command to run and do the main things that Burp is created for. Also i'm addicted to coding... so yeah.


# Disclaimer

This tool is still in development phase and lacks many useful features. I'm actively developing it for my personal use so make sure to watch for changes. Any contribution is appreciated. And you can always reach to me at my [X](https://x.com/Ch1y0w0)

**Note: (HTTPS support is in progress)**

# ToDo List
	[X] ~~Fix Forwarding Back to Browser~~
	[X] ~~Not Working On All Hosts~~
	[ ] Modify Packets
	[ ] HTTPS (Certificate generation)
	[X] ~~Full Rework~~