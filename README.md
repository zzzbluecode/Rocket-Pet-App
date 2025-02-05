<div align="center">

<img src="https://github.com/zzzbluecode/RocketPetApp/blob/main/rocket_ai.png" width="400">
<h2>Rocket Pet App</h2>
<p>A rocket pet traces your mouse.</p>
<img src="https://github.com/user-attachments/assets/d1f5d5f0-b6dc-41c6-a91d-c6c37ed325bb" width="800">
</div>

# setup
```
pip install Pillow psutil
```

# run
```
python RocketPetApp.py
```

# play with the demo
just click the exe file (only for win os)

# build
set USER_RESOURCE_MONITOR = False to save resources

use auto-py-to-exe to build the exe
```
pip install auto-py-to-exe
```
```
auto-py-to-exe
```

- Script Location
  - select RocketPetApp.py script

- Onefile
  - One Directory: allow yous to change the rocket image
  - One File: will just output a single exe file. good for directly use

- Console Window
  - Console: good for debug
  - Window: work like a normal app

- Additional FIles
  - Add Icon: add the rocket ico file
  - Add Files: add the rocket png file

- convert to exe
  - press convert button

# Current Command
```
pyinstaller --noconfirm --onefile --windowed --icon "D:\zzzbluecode\RocketPetApp\rocket_ai.ico" --add-data "D:\zzzbluecode\RocketPetApp\rocket_ai.png;."  "D:\zzzbluecode\RocketPetApp\RocketPetApp.py"
```

# remark
## the exe start slow at the first time
it is normal

## run exe error
got SyntaxError: Non-UTF-8 code starting with '\x90' in file...
added below to RocketPetApp.py to prevent run exe error
```python
# -*- coding: utf-8 -*- ~
```

## to refresh the ico in taskbar for win os 
https://superuser.com/questions/499078/refresh-icon-cache-without-rebooting

for win10: 
```
ie4uinit.exe -show
```

# tools
## assist in code generation and optimization
https://poe.com/
https://www.deepseek.com/
https://www.blackbox.ai/

## generate image
https://www.png.ai/

## convert image file format
https://convertio.co/

## remove background
https://www.imagine.art/bg-remover

## crop image
https://www.iloveimg.com/crop-image

## rotate image
https://www.resizepixel.com/edit?act=rotate
