import bpy
import numpy as np
import scipy.io
import scipy.misc
from mathutils import Vector
import sys
import argparse
import json
from contextlib import redirect_stdout
import datetime
from PIL import Image
from tqdm import tqdm

#Helper calss to allow defining alternate detector planes     
class Dimensions:
    def __init__(self, dimensions, x, y, z):
        self.xmin = dimensions[x][0]
        self.xmax = dimensions[x][1]
        self.ymin = dimensions[y][0]
        self.ymax = dimensions[y][1]
        self.zmin = dimensions[z][0]
        self.zmax = dimensions[z][1]
        self.x = x
        self.y = y
        self.z = z
        
def get_ordered_coordinates(coords, dimensions):
    ordered =[0,0,0]
    ordered[dimensions.x] = coords[0]
    ordered[dimensions.y] = coords[1]
    ordered[dimensions.z] = coords[2]
    return ordered
    
def get_pixel_coordinates(mn,mx,sz):
    return np.linspace(mn, mx,sz+2)[1:-1]
        
def update_matrix_with_density(matrix, size, dimensions, att):
    #Initilaize the matrix indexes
    j=-1
    mw = bpy.context.object.matrix_world
    mwi = mw.inverted()
    stepsize = 1e-4
    #run through x,y coordinates
    for x in get_pixel_coordinates(dimensions.xmin, dimensions.xmax,size):
        j+=1
        i=-1

        for y in np.flip(get_pixel_coordinates(dimensions.ymin, dimensions.ymax,size)):
            i+=1
            #x-ray src
            origin = mwi @ Vector(get_ordered_coordinates((x,y,dimensions.zmin-1),dimensions))
            #detector 
            dest = mwi @ Vector(get_ordered_coordinates((x,y,dimensions.zmax+1),dimensions))
            
            #ray direction
            direction = (dest - origin).normalized()
            
            #is the object hit?, the hit location, the normal, the face
            ishit, location_1, normal, face = bpy.context.object.ray_cast(origin, direction)
            
            #as long as we hit the object
            hitcount = 0
            while ishit:
                hitcount +=1
                #move the ray cast origin slightly along the ray from the hit point to get the second point
                ishit, location_2, normal, face = bpy.context.object.ray_cast(location_1+stepsize*direction, direction)
                if location_1 == location_2:
                    print("Error: hit same location twice")
                #if nothing is hit then there is an error - like the object has no back side
                if not ishit:
                    print(f'Warning: no second hit. Depth not within threshhold of {stepsize}')
                
                else:
                    #If we have both locations then calculate the attenuation by multiplying the depth of the intersection with density         
                    hitcount+=1
                    if location_1 is not None and location_2 is not None :
                        attenuation = (location_1-location_2).length*att
                        matrix[i,j]+=attenuation
                    #If one of them is None something strange is going on
                    else:
                        print("Raycast error 2, hit is None")
                    #See if we hit more of the object (we might be dealing with two or more layers of tail)
                    ishit, location_1, normal, face = bpy.context.object.ray_cast(location_2+stepsize*direction, direction)



#def generate_radiograph(theta, dimensions, size, rotation_axis, image_number, att):
#        #Rotate the object instead of 'gantry'
#        #bpy.context.object.rotation_euler[rotation_axis] = theta
#        bpy.context.view_layer.update()
#        
#        parent = bpy.context.view_layer.objects.active
#        
#        #generate image
#        matrix = np.zeros((size,size))
#        for obj in parent.children:
#        	bpy.context.view_layer.objects.active = obj
#        	update_matrix_with_density(matrix, size, dimensions, att)
##        bpy.context.view_layer.objects.active = parent
#        image_name = format(bpy.context.scene.frame_current, '03d') + format(image_number, '05d') + ".npy"
#        np.save(bpy.context.scene.render.filepath+image_name, matrix)
        
        #unrotate
        #bpy.context.object.rotation_euler[rotation_axis] = 0
#        bpy.context.view_layer.update()


#def generate_sinogram(size, rotation_axis, thetas, dimensions, angles_per_frame, att):
#    thetastart = angles_per_frame*(bpy.context.scene.frame_current-bpy.context.scene.frame_start)
#    thetacount = len(thetas) if angles_per_frame == 0 else angles_per_frame
#    thetaend = thetastart+thetacount
#    for i in range(thetastart,thetaend):
#        j = i % len(thetas)
#        theta = thetas[j]
#        generate_radiograph(theta, dimensions, size, rotation_axis, j, att)


def main(argv):
    parser = argparse.ArgumentParser(description="Generate simulated x-ray data of mesh assuming attenuation of 1 per blender unit. The start and endframe and active scene and output file are selected through Blender arguments.")
    parser.add_argument('-a', '--att', help="attenuation pr. blender unit", default = 0.5, type=float)
    parser.add_argument('-xax', '--xaxis', help="first picture plane axis", default = 1, type=int)
    parser.add_argument('-yax', '--yaxis', help="second picture plane axis", default = 2, type=int)
    parser.add_argument('-zax', '--zaxis', help="axis parallel to rays", default = 0, type=int)
    #parser.add_argument('-rax', '--raxis', help="rotation axis (first or second picture plane axis)", default = 2, type=int)
    parser.add_argument('-ra', '--radius', help="radius for raycasting", default = 3, type=int)
    parser.add_argument('-px', '--numpixels', help="set number of pixels", default = 128, type=int)
    parser.add_argument('-n', '--meshname', help="name of mesh", default = "mesh")
        
    args, unknown = parser.parse_known_args(argv)
    
    #save the arguments along side the renders so we know the specifics of the data
    with open(bpy.context.scene.render.filepath+'output.txt', 'a+') as f:
        with redirect_stdout(f):
            print(datetime.datetime.now())
            parser.print_help()
            print('\n'+json.dumps(vars(args)))
            print('\n')

    bpy.context.view_layer.objects.active = bpy.data.objects[args.meshname]


    dimensions = Dimensions(((-args.radius,args.radius),(-args.radius,args.radius),(-args.radius,args.radius)),args.xaxis,args.yaxis,args.zaxis)
    parent = bpy.context.view_layer.objects.active
    #geneerate images for specified frames
    for frame in tqdm(range(bpy.context.scene.frame_start, bpy.context.scene.frame_end+1)):
        bpy.context.scene.frame_set(frame)
                
    
        #generate image
        matrix = np.zeros((args.numpixels,args.numpixels))
        if len(parent.children) > 0:
            for obj in parent.children:
                bpy.context.view_layer.objects.active = obj
                update_matrix_with_density(matrix, args.numpixels, dimensions, args.att)
        else: 
            bpy.context.view_layer.objects.active = obj
            update_matrix_with_density(matrix, args.numpixels, dimensions, args.att)
        
        image_name = format(bpy.context.scene.frame_current, '06d') + ".npy"
        np.save(bpy.context.scene.render.filepath+image_name, matrix)
        bpy.context.view_layer.objects.active = parent


if __name__ == '__main__':
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    main(argv)
