import os
import shutil

def copy_files(dir1, dir2, file_mapping):
    # Ensure dir2 exists
    os.makedirs(dir2, exist_ok=True)

    for key, value in file_mapping.items():
        source = os.path.join(dir1, value)
        destination = os.path.join(dir2, key)

        # Check if the source file exists
        if not os.path.exists(source):
            print(f"Warning: Source file '{source}' does not exist.")
            continue

        # Copy the file
        try:
            shutil.copyfile(source, destination)
            print(f"Copied '{source}' to '{destination}'")
        except IOError as e:
            print(f"Unable to copy. Error: {e}")

# Example usage
dir1 = "PNG/128"
dir2 = "128"
file_mapping = {
"Cloudy.png":"cloudy.png",				
"HeavyShowers.png":"rain.png",		      
"LightRain.png":"day_rain.png",			     
"LightSleetShowers.png":"day_sleet.png",  
"PartlyCloudy.png":"day_partial_cloud.png",  
"ThunderyHeavyRain.png":"rain_thunder.png",    
"Unknown.png":"Unknown.png",
"Fog.png":"fog.png",        
"LightShowers.png":"snow.png",  
"LightSnow.png":"snow.png",          
"ThunderyShowers.png":"thunder.png",      
"VeryCloudy.png":"overcast.png",
"HeavyRain.png":"rain.png",  
"LightSleet.png":"day_sleet.png",    
"LightSnowShowers.png":"day_rain.png",   
"Sunny.png":"day_clear.png",         
"ThunderySnowShowers.png":"snow_thunder.png",
}

copy_files(dir1, dir2, file_mapping)


