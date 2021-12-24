# Colltecitons of some useful stuff
The following tools listed bellow are mainly for better use [mangoct](https://github.com/ustcfdm/mangoct).
### 1. postfix change
```angular2html
./postfix_change/toRaw.py
```
Mainly used to modify the files' postfix in the folder.

Usage: use '--help' to show the hint, or:
```angular2html
python toRaw.py -d your-folder -p your-postfix
```
### 2. preprocess
```angular2html
./preprocess/proj2sinogram.py
```
[mangoct](https://github.com/ustcfdm/mangoct) only accept sinogram, so when use cone beam reconstruction, keep the y axis the same and look at the x and V axes to construct sinogram. In other words, do the following change:

postlog_img(x, y, V) => postlog_img(x, V, y).

You can also use 'proj2sinogram.py' to do simple air correction, see 'config_helper.yml' for more config information.

Usage: use '--help' to show the hint, or:
```angular2html
python proj2sinogram.py -d config_helper.yml
```