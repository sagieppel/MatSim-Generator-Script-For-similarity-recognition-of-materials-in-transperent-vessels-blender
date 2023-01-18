


## Description:
# This script will procedurally generate images of randomly shaped transparent vessels with random objects or simulated liquid inside the vessel with gradual transfomration of material on the object content for the matsim dataset. 



#### This was run with Blender 3.4 with no additional add-ons

### Where to start: 
#The best place to start is in the “Main” section in the last part of this script.

### What needed:  
#Objects Folder, HDRI background folder, and a folder of PBR materials (Example folders are supplied as: “HDRI_BackGround”, “PBRMaterials”, and “Objects”)

## How to use:
#1) Go to the “Main” section of the python script, in the “input parameter” subsection.
#2) In the "OutFolder" parameter set path to where the generated images should be saved.
#3) Set Path HDRI_BackGroundFolder," parameter set path to where the background HDRI (for a start, use the example HDRI_BackGround, supplied)
#4) In the "PBRMaterialsFolder" parameter set path to where the PBR materials (for a start, use the example PBRMaterials folder supplied)
#5) In the "ObjectsFolder" parameter, set the path to where the objects file are saved (for a start, use the example object folder supplied).
#6) Run the script from Blender or run the script from the command line 
#Images should start appearing in the OutFolder after few minutes (depending on the rendering file). 
#Note that while running, Blender will be paralyzed.

## Additional parameters 
#(in the “Input parameters” of "Main" python script  (near the end of this file)
#"NumSimulationsToRun" determines how many different environments to render into images (How many different sets will be created).
# ContentMode  Will determine the type of content that will be generated insid the vessel liquid or objce
#"Objects":   objects inside the vessel (objects will be taken from the Objects folder)
#"FlatLiquid": will create simple liquid with flat surface that fill the bottum of the vessel (no liquid simulation will be performed)
###############################Dependcies######################################################################################3

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import json
import sys
filepath = bpy.data.filepath
homedir = os.path.dirname(filepath)
#sys.path.append("/home/breakeroftime/Desktop/Simulations/ModularVesselContent")
sys.path.append(homedir)
os.chdir(homedir)
import VesselGeneration as VesselGen
import LiquidSimulation as LiquidSim
import MaterialsHandling as Materials
import ObjectsHandling as Objects
import RenderingAndSaving as RenderSave
import SetScene
import colorsys


################################################################################################################################################################

#                                    Main 

###################################################################################################################################################################

# Example HDRI_BackGroundFolder and PBRMaterialsFolder  and ObjectsFolder folders should be in the same folder as the script. 
#------------------------Input parameters---------------------------------------------------------------------

# Example HDRI_BackGroundFolder and PBRMaterialsFolder  and ObjectsFolder folders should be in the same folder as the script. 
# Recomand nto use absolute and not relative paths  as blender is not good with these

 
#HDRI_BackGroundFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/4k/" 
##
##"HDRI_BackGround/"
##r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/4k/" 
##ObjectFolder=r"/home/breakeroftime/Documents/Datasets/Shapenet/ShapeNetCoreV2/"
##Folder of objects (like shapenet) 
#ObjectFolder=r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/" 
##r"Objects/"
##r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/" 
## folder where out put will be save
#OutFolder="OutFolder_OBJ_IN_VESSELS/" # folder where out put will be save
#pbr_folders = [r"/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR/",
#r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/']
##r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/',
##r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/']
#image_dir=r"/home/breakeroftime/Documents/Datasets/ADE20K_Parts_Pointer/Eval/Image/"

#UseGPU_CUDA=True
##ContentMode= "Object" 
 

#pbr_folders = [ 
#r"/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR/",
#r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/',
#r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/',
#r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/']

#------------------Input parameters--------------------------------------------------------------------------------------
OutFolder=homedir+r"/Output/"# Where output images will be saved
HDRI_BackGroundFolder="HDRI_BackGround/"# Background hdri folder
ObjectFolder=r"Objects/" # Folder with objects
pbr_folders = ['PBRMaterials/'] # folders with PBR materiall each folder will be use with equal chance
UseGPU_CUDA=True
NumSimulationsToRun=20# Number of sets to render
DontOveride=True # dont overide existing renders
ContentMode = "FlatLiquid"#"Object" #"FlatLiquid" #Type of content that will be generated insid the vessel can be "FlatLiquid" or an "Object"
use_priodical_exits = False# Exit blender once every few sets to avoid memory leaks, assuming that the script is run inside Run.sh loop that will imidiatly restart blender fresh

#------------------Create PBR list-------------------------------------------------------- 
materials_lst = [] # List of all pbr materials folders path
for fff,fold in enumerate(pbr_folders): # go over all super folders 
    materials_lst.append([]) 
    for sdir in  os.listdir(fold): # go over all pbrs in folder
        pbr_path=fold+"//"+sdir+"//"
        if os.path.isdir(pbr_path):
              materials_lst[fff].append(pbr_path)

#------------------------------------Create list with all hdri files in the folder-------------------------------------
hdr_list=[]
for hname in os.listdir(HDRI_BackGroundFolder): 
   if ".hdr" in hname:
         hdr_list.append(HDRI_BackGroundFolder+"//"+hname)
#---------------------Other  optional parameters-------------------------------------------------------








#SaveObjects=False # Do you want to save vessel and content as objects, some of these filese can  be large


#==============Set Rendering engine parameters (for image creaion)==========================================

bpy.context.scene.render.engine = 'CYCLES' # Use this configuration if you want to be able to see the content of the vessel (eve does not support content)
#bpy.context.scene.cycles.device = 'GPU'
#bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL' # Not sure if this is really necessary but might help with sum surface textures
bpy.context.scene.cycles.samples = 120 #200, #900 # This work well for rtx 3090 for weaker hardware this can take lots of time
bpy.context.scene.cycles.preview_samples = 900 # This work well for rtx 3090 for weaker hardware this can take lots of time

bpy.context.scene.render.resolution_x = 800 # Image resolution
bpy.context.scene.render.resolution_y = 800

#bpy.context.scene.eevee.use_ssr = True
#bpy.context.scene.eevee.use_ssr_refraction = True
bpy.context.scene.cycles.caustics_refractive=True
bpy.context.scene.cycles.caustics_reflective=True
bpy.context.scene.cycles.use_preview_denoising = True
bpy.context.scene.cycles.use_denoising = True


# materials graphs that will no be deleted between scene
MaterialList=["White","Black","PbrMaterial1","PbrMaterial2","TwoPhaseMaterial","GroundMaterial","TransparentLiquidMaterial","BSDFMaterial","BSDFMaterialLiquid","Glass","PBRReplacement"] # Materials that will be used

#-------------------------Create delete folders--------------------------------------------------------------

#CountFolder=OutFolder+"/count/" # Folder for remembring image numbers (for restarting script without over running existing files)
#CatcheFolder=OutFolder+"//Temp_cache//" # folder where liquid simulation will be saved (this will be deleted every simulation
if not os.path.exists(OutFolder): os.mkdir(OutFolder)

#----------------------------Create list of Objects that will be loaded during the simulation---------------------------------------------------------------
ObjectList={}
if os.path.isdir(ObjectFolder):
    ObjectList=Objects.CreateObjectList(ObjectFolder)

#------------------Set GPU----------------------------------------------------
if UseGPU_CUDA:
   bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA" # or "OPENCL"

   # Set the device and feature set

   bpy.context.scene.cycles.device = "GPU"
   # get_devices() to let Blender detects GPU device
   bpy.context.preferences.addons["cycles"].preferences.get_devices()

######################Main loop for creating images##########################################################
# loop 1: choose pair of materials, loop 2, create vessel content and scene, loop 3: change materials ration and render
scounter=0 # Counter For breaking and exiting program once in a while (to clean the system, its complicated)
for cnt in range(NumSimulationsToRun):
#-------------------------------------------------------------------   
    MainOutputFolder=OutFolder+"/"+str(cnt)
    print("1) make dir")
    if  os.path.exists(MainOutputFolder) and DontOveride: continue # Dont over run existing folder continue from where you started
    os.mkdir(MainOutputFolder)
#----------Select method to uv map material into object surface-----------------------------------
    print("2 select materials and mapping")
    if random.random()<0.8: #  'camera' 'generated' 'object'
       uv='camera'
    else: 
       uv='object'
    # Pick material type PBR/bsdf
    if random.random()<0.8: 
           matype1='pbr'
    else:
           matype1='bsdf'
    if random.random()<0.8: 
           matype2='pbr'
    else:
           matype2='bsdf'
    
    # load  uv into material graph
           
    Materials.ChangeUVmapping(bpy.data.node_groups['Phase1'],uvmode = uv) 
    Materials.ChangeUVmapping(bpy.data.node_groups['Phase2'],uvmode = uv)
    
           
#    matype1='pbr'
#    matype2='pbr'
   # load_random_material(pbr_folders[rnd],materials_lst[rnd], "NodeGroupPBR_Generated" )
     
    # load random material
    MaterialDictionary={} # Where materials name and properties will be stored                      

    MaterialDictionary['material1']=Materials.ChangeMaterialMode(bpy.data.node_groups['Phase1'],matype1,materials_lst) # Change the type of material by connecting bsdf, pbr, or value 0-255 node to the output node 
    MaterialDictionary['material2']=Materials.ChangeMaterialMode(bpy.data.node_groups['Phase2'],matype2,materials_lst)
    with open(MainOutputFolder +"//MaterialsNamesAndProperties.json", "w") as outfile: json.dump(MaterialDictionary, outfile)  
###################################################################################
#---------------------Create scenes containing transition between the two materials choosed--------------------------------------------   
    RotateMaterial= random.random()<0.7 # rotate material between frames
    print("3) start making scene")
    for nscenes in range(6): # different scenes same materials each scene will contain gradual transition between the materials on single or sevral objects
        MainOutputFolder
        print("Add material")
       # SubDivResolution=MinSubDivisionResolution+np.random.randint(MaxSubDivisionResolution-MinSubDivisionResolution)
    #    if np.random.rand()<0.1: SubDivResolution=MaxSubDivisionResolution
     #   TimeStep=MinTimeStep+np.random.randint(MaxTimeStep-MinTimeStep) 
    #    if np.random.rand()<0.2: TimeStep=MinTimeStep
        
        
     #   if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation folder to free space
     ##   if NumSimulationsToRun==0: break
        OutputFolder= MainOutputFolder+"/Scene_"+str(nscenes)+"/"
    #    if  os.path.exists(OutputFolder): continue # Dont over run existing folder continue from where you started
        os.mkdir(OutputFolder) 
###        NumSimulationsToRun-=1

        ContentMaterial={"TYPE":"NONE"}

    #    #================================Run simulation and rendering=============================================================================
        print("=========================Start====================================")
        print("Simulation number:"+str(cnt)+" Remaining:"+ str(NumSimulationsToRun))
        SetScene.CleanScene()  # Delete all objects in scence
        print("4) load object and content and set scnee") 
      
    #    #------------------------------Create random vessel object and assign  material to it---------------------------------
        MaxXY,MaxZ,MinZ,VesselWallThikness,ContentHeight=VesselGen.AddVessel("Vessel","Content",ScaleFactor=1, SimpleLiquid=(ContentMode=="FlatLiquid")) # Create Vessel object named "Vessel" and add to scene also create mesh inside the vessel ("Content) which will be transformed to liquid
        VesselMaterial=Materials.AssignMaterialToVessel("Vessel") # assign random material to vessel object
        if ContentMode == "Object": # Add object as vessel content
               bpy.data.objects.remove( bpy.data.objects["Content"]) # Remove original content (generated with the vessel)
               ContentNames=Objects.LoadNObjectsInsideVessel(ObjectList,MaxXY-VesselWallThikness,MinZ,MaxZ,NumObjects=random.randint(1,3)) # Put random objects in vessel
               bpy.data.objects[ContentNames[0]].name="Content"
               
               # remove overlapping faceses
               bpy.ops.object.select_all(action="DESELECT")
               bpy.data.objects["Content"].select_set(True)
               bpy.context.view_layer.objects.active = bpy.data.objects["Content"]
               bpy.ops.object.editmode_toggle() #edit mode
               bpy.ops.mesh.remove_doubles() #remove overlapping faces
       
               bpy.ops.uv.smart_project(island_margin=0.03)
               bpy.ops.object.editmode_toggle() #back to object mode
              
       #-------------------------------------------Create ground plane and assign materials to it----------------------------------
        if np.random.rand()<0.33:
            PlaneSx,PlaneSy= SetScene.AddGroundPlane("Ground",x0=0,y0=0,z0=-VesselWallThikness*(np.random.rand()*0.75+0.25)-0.1,sx=MaxXY,sy=MaxXY) # Add plane for ground
            if np.random.rand()<0.8:
                Materials.load_random_PBR_material(bpy.data.materials['GroundMaterial'].node_tree,materials_lst)
                Materials.ReplaceMaterial(bpy.data.objects["Ground"],bpy.data.materials['GroundMaterial'])  
            else: 
                Materials.AssignMaterialBSDFtoObject(ObjectName="Ground",MaterialName="BSDFMaterial") 
        else: 
            with open(OutputFolder+'/NoGroundPlane.txt', 'w'): print("No Ground Plane")
            PlaneSx,PlaneSy=MaxXY*(np.random.rand()*4+2), MaxXY*(np.random.rand()*4+2)
    #------------------------Load background hdri---------------------------------------------------------------   
        SetScene.AddBackground(hdr_list) # Add randonm Background hdri from hdri folder

    #..............................Create load objects into scene background....................................................
        if np.random.rand()<0.25:
                   Objects.LoadNObjectsToScene(ObjectList,AvoidPos=[0,0,0],AvoidRad=MaxXY,NumObjects=np.random.randint(11),MnPos=[-PlaneSx,-PlaneSy,-5],MxPos=[PlaneSx,PlaneSy,0],MnScale=(np.random.rand()*0.8+0.2)*MaxXY,MxScale=np.max([MaxXY,MaxZ])*(1+np.random.rand()*4))    
        
    ##################################Create vessel content could be a liquid or object##########################################
        ContentNames=["Content"] # names of all meshes/objects inside vessels
      #  FramesToRender=[0]  # Frames in the animation to render 

    #------------------Set material content------------------------------------------------------------------
        obj=bpy.data.objects["Content"]
        Materials.ReplaceMaterial(obj,bpy.data.materials['TwoPhaseMaterial'])     
    #-----------------Save materials properties as json files------------------------------------------------------------
        if not  os.path.exists(OutputFolder): os.mkdir(OutputFolder)
        print("+++++++++++++++++++++Content material++++++++++++++++++++++++++++++")
        print(ContentMaterial)
        if ContentMaterial["TYPE"]!="NONE":
                  with open(OutputFolder+'/ContentMaterial.json', 'w') as fp: json.dump(ContentMaterial, fp)
        print("+++++++++++++++++++++vessel material++++++++++++++++++++++++++++++")
        print(VesselMaterial)
        with open(OutputFolder+'/VesselMaterial.json', 'w') as fp: json.dump(VesselMaterial, fp)

    #...........Set Scene and camera postion..........................................................
        SetScene.RandomlySetCameraPos(name="Camera",VesWidth = MaxXY,VesHeight = MaxZ)
        with open(OutputFolder+'/CameraParameters.json', 'w') as fp: json.dump( SetScene.CameraParamtersToDictionary(), fp)
                
######################################################################################################################3

# Generate images of same scene with different materials ratio

##########################################################################################################################        
        print("5) rendner gradual tranisition")
        for matsRatio in [0,0.25,0.5,0.75,1]:      
                print("materials ratio",matsRatio)
            #------------Modify scene scene----------------------------------------------------------------------------------  
                if nscenes>1: 
                    SetScene.RandomRotateBackground() # for scene beyond 2 start randomly  rotating background between scenes
                if nscenes>3: 
                    SetScene.AddBackground(hdr_list)# for scene beyond 3 replace background between frames  
                      
                Materials.Randomize_RotateTranslate_PBR_MaterialMapping(bpy.data.node_groups["Phase1"].nodes,RotateMaterial) # Randomly rotate and translate material mapping on object
                    
                Materials.Randomize_RotateTranslate_PBR_MaterialMapping(bpy.data.node_groups["Phase2"].nodes,RotateMaterial)# Randomly rotate and translate material mapping on object
                
                bpy.data.materials["TwoPhaseMaterial"].node_tree.nodes["Mix Shader"].inputs[0].default_value = bpy.data.materials["TwoPhaseMaterial"].node_tree.nodes["Mix Shader"].inputs[0].default_value = matsRatio # Choose mixing ratio between two materials
                obj=bpy.data.objects["Content"]
        
 
            #------------------------------------------------------Save Objects to file-----------------------------------------------------
            #-------------------------------------------------------Render Save images--------------------------------------------------------------    
                
                bpy.context.scene.render.engine = 'CYCLES'
                print("Saving Images")
                print(OutputFolder)
                Objects.HideObject("VesselOpenning",Hide=True)  # Hide vesel oopning surface
                RenderSave.RenderImageAndSave(FileNamePrefix="RGB_"+str(matsRatio),OutputFolder=OutputFolder) # Render images and Save vessel content with no vessel

                   
                #-------------------Save segmentation data for phases---------------------------------------------------------------------    
                bpy.context.scene.render.engine = 'BLENDER_EEVEE'
             
                bpy.context.scene.render.image_settings.file_format = 'PNG'
               # Objects.HideObject("Vessel",Hide=True)
                
                #----Remove all objects accept content-------------------
                #objs=[]
#                for nm in bpy.data.objects: objs.append(nm)
#                for nm in objs: 
#                    if (nm.name  not in ContentNames) and (nm.name!='Camera'): 
#                        bpy.data.objects.remove(nm)
                #for nm in ContentNames:  Objects.HideObject(nm,Hide=False)
                #----Remove all objects accept content-------------------    
                  
#              
#                bpy.context.scene.render.filepath = OutputFolder +'/' + "ContentMask"
#                bpy.ops.render.render(write_still=True)
#                print("-------------------",bpy.ops.render.filepath) 
                   
                            
                # Write materials properties
           

    # #------------------------Create segmentation map----------------------------------------------------------------------------------------------
        
       # bpy.context.scene.world= bpy.data.worlds['BackgroundBlack'] # Set Background to black
       # save vessel mask
        Objects.HideObject("VesselOpenning",Hide=True) 
        Objects.HideObject('Content',Hide=True)
        RenderSave.SaveObjectVisibleMask(["Vessel"],OutputFolder + "VesselMaskOcluded")
        RenderSave.SaveObjectFullMask(["Vessel"],OutputFolder + "VesselMaskFull")
        
        # save content mask
        Objects.HideObject("VesselOpenning",Hide=True) 
        Objects.HideObject('Vessel',Hide=True)
        Objects.HideObject('Content',Hide=False)
        RenderSave.SaveObjectVisibleMask(["Content"],OutputFolder + "ContentMaskOcluded")
        RenderSave.SaveObjectFullMask(["Content"],OutputFolder + "ContentMaskFull")
        
        open(OutputFolder+"/Finished.txt","w").close()
        # remove all objects from scene (but keep materials for next scene)
        objs=[]
        for nm in bpy.data.objects: objs.append(nm)
        for nm in objs:  
                bpy.data.objects.remove(nm)
       
    #------------------------------Finish and clean data--------------------------------------------------
        

    print("Cleaning")

    open(MainOutputFolder+"/Finished.txt","w").close()
    
    # Clean images
    imlist=[]
    for nm in bpy.data.images: imlist.append(nm) 
    for nm in imlist:
        bpy.data.images.remove(nm)
    # Clean materials
    mtlist=[]
    for nm in bpy.data.materials: 
        if nm.name not in MaterialList: mtlist.append(nm)
    for nm in mtlist:
        bpy.data.materials.remove(nm)
 #   if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation catche folder to free space
    print("========================Finished==================================")
    SetScene.CleanScene()  # Delete all objects in scence
    scounter+=1
    if use_priodical_exits and scounter>=12: # Break program and exit blender, allow blender to remove junk, otherwise the program might start to slow down (assume it run in loop inside run.sh)
            #  print("Resting for a minute")
            #  time.sleep(30)
              break
if use_priodical_exits:
   print("quit by priodic exit")
   bpy.ops.wm.quit_blender()