while true
do
   echo "Running blender"
   blender DatasetGeneration.blend -b -P  main.py --background
   echo "Crushed"
done


