while true
do
   echo "Running blender"
   blender DatasetGeneration.blend -b -P  --background  main.py 
   echo "Crushed"
done


