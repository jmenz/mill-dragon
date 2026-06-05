# Linuxcnc mill controller

## Disclaimer:
This is my personal hobby project. You can use it or any of its parts at your own risk. I'm not responsible for any damage to your equipment or your injury.

### install custom hall components:

```
sudo halcompile --install comp/RP1.c
```


### TOUCH:

To hide cursor when touch used
```
sudo apt install unclutter-xfixes
```
and add to autoload:
```
unclutter --hide-on-touch
```

### Additional:

Install Py debugger
```
sudo apt install python3-debugpy
```