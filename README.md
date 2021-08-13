This is a simple script for using blender to create parallel beam phantom data. It is especially useful for creating dynamic phantoms and slightly more complex 3D phantoms than what can be done in python alone.

## Getting started

1. Download the script and make sure blender is installed and added to path
2. You might need to install some libraries to your blender python. See below how this can be done.
3. Make a blender model, and rotate it linearly according to your wanted acquisition scheme. Make sure everything you want in the simulation is attached to a common parent PARENT. Save your simulation as YOURFILENAME.blend (see particle_test_4.blend for an example)
4. Then run blender in the background with the xraysim script like this:

blender YOURFILENAME.blend --frame-start 1 --frame-end 240 -o output/TEST/ --background --python xraysim.py -- -n PARENT --radius 2 -px 512

You need to specify which frames (--frame-start 1 --frame-end 240) you want included, where to save output (-o) as .npy, and which object to include (-n), all children will be included as well.
You also specify the radius (in blender units) (--radius) from blender origo to detector position, and the number of pixels (-px) you want in your resulting data (the resulting matrix will have -px columns and -px rows).
Use --help for more options.


## Installing python libraries to work with blender
DO NOT USE ANACONDA! It does not work.

Instead install pip for the python bundled with blender and use pip to install required packages.

First of all, pip is not part of Python so it doesn't come by default with Blender.

It has to be installed for Blender's bundled Python even if you already have pip for some other version of Python on your system.
For this get the get-pip.py file from the pip documentation and save it in \blender-path\2.xx\python\bin\python
. 
You'll find the blender python binary at:

\blender-path\2.xx\python\bin\python
Use this binary to run the get-pip.py. Open cmd prompt, cd to the python folder in the blender instalation, then cd to \bin and write:

python get-pip.py

You should now have pip installed for blender. 
You use it with blenders python and you have to point to the pip that was installed for blenders python. 
Both are in blenders folder tree and you use them like this:

cd to \blender-path\c.xx\python then write
bin\python lib\site-packages\pip install scipy

This installs scipy for your blenders python. Of course you have to adjust names according to the version you use.
