#write a python program which has 3 input files:
#definition.csv
#provinces.bmp
#terrain.bmp

#definition.csv will always be in this format
#{province number};{r};{g};{b};{land/sea/lake};{true/false};{terrain};1
#{r} {g} and {b} represent an rgb color associated with the province.
#{terrain} can either be desert, hills, mountain, marsh, forest, jungle, plains, or urban.

#provinces.bmp is an image file which shows all of the different provinces. The color of each tile will point to a specific province number in the definition.csv file.

#terrain.bmp is an image file which is has identical dimensions to province.bmp. This file helps determine what terrain type each province should be. For land terrain types, the colors are
#plains = #FF8142 = (255, 129, 66)
#forest = #59C755 = (89, 199, 85)
#hills = #F8FF99 = (248, 255, 153)
#jungle = #7FBF00 = (127, 191, 0)
#marsh = #4C6023 = (76, 96, 35)
#mountain = #7C877D = (124, 135, 125)
#desert = #FF3F00 = (255, 63, 0)
#urban = #9B00FF = (155, 0, 255)

#The python program should do the following:
#STEP 1: Look at the first province in the definitions list, find the RGB value. If the province is lake or sea, skip and go to the next province.
#STEP 2: Find the province on provinces.bmp
#STEP 3: Cross reference this location onto terrain.bmp. Determine which terrain color is most prevalent (if it is tied, choose between the tie randomly).
#STEP 4: Record this onto a new file called "OUTPUT.csv"

# ideas: import csv as a dataframe
# write output file as you go?

import pandas as pd
from PIL import Image
import os
import numpy as np
from collections import Counter
from random import choice
import signal
import sys


stopped = False

def handle_interrupt(signal, frame):
    global stopped
    stopped = True
    print("\nProcess interrupted. Saving progress... Please wait.")

def find_dominant_terrain(rgb, provinces, terrain_pixels):
    color_codes = {
        (255, 129, 66): "plains",
        (89, 199, 85): "forest",
        (248, 255, 153): "hills",
        (127, 191, 0): "jungle",
        (76, 96, 35): "marsh",
        (124, 135, 125): "mountain",
        (255, 63, 0): "desert",
        (155, 0, 255): "urban"
    }


    province = np.all(provinces == rgb, axis=1)
    if not np.any(province):
        return None
    
    terrain = terrain_pixels[province]
    terrain_list = terrain.tolist()
    terrain_tup = list(map(tuple, terrain_list))


    occurrances = Counter(terrain_tup)
    dominant_terrain_rgb = occurrances.most_common(1)[0][0]

    dominant_terrain_readable = color_codes.get(dominant_terrain_rgb)

    return dominant_terrain_readable

def save_progress(output_path, definition_df):
    definition_df.to_csv(output_path, index=False, header=False)

def loop_through_definitions(definition_df, provinces, terrains, output_path):
    global stopped

    

    print(f"Processing {len(definition_df)} provinces...\n")
    for idx, i in definition_df.iterrows():
        if stopped:
            break

        print(f"Processing province {idx}/{len(definition_df)}: Province Number {i['idx']}")
        if i["type"] in ["sea", "lake"] or i["terrain"] in ["land", "sea", "lake"] or i["is_coastal"]:
            print(f"  Skipping province {i['idx']} (type: {i['type']} or coastal status: {i['is_coastal']}).")
            continue

        # Determine the dominant terrain type from the terrain.bmp file
        dominant_terrain = find_dominant_terrain([i["rgb1"], i["rgb2"], i["rgb3"]], provinces, terrains)

        if dominant_terrain is not None and dominant_terrain != i["terrain"]:
            # Update the terrain in the original row
            print(f"  Updating terrain for province {i['idx']}: {i['terrain']} -> {dominant_terrain}")

            definition_df.iloc[idx, definition_df.columns.get_loc("terrain")] = dominant_terrain #change df in place

    if stopped:
        print(f"Process interrupted. Partial progress saved to '{output_path}'.")
    else:
        print(f"Processing complete. Updated data saved to '{output_path}'.")
    save_progress(output_path, definition_df)
    


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)

    provinces_path = os.path.dirname(__file__) + "\\provinces.bmp"
    terrain_path = os.path.dirname(__file__) + "\\terrain.bmp"
    definition_path = os.path.dirname(__file__) + "\\definition.csv"
    output_path = os.path.dirname(__file__) + "\\output.csv"

    provinces_bmp = Image.open(provinces_path)
    terrain_bmp = Image.open(terrain_path)

    provinces_pixels = np.array(provinces_bmp)
    provinces_pixels = provinces_pixels.reshape(-1, provinces_pixels.shape[-1]) #2d array containing arrays of pixels (rgb)

    terrain_pixels = np.asarray(terrain_bmp)
    terrain_pixels = terrain_pixels.reshape(-1, terrain_pixels.shape[-1])

    definition_df = pd.read_csv(definition_path, sep=";", names=["idx", "rgb1", "rgb2", "rgb3", "type", "is_coastal", "terrain", "bool"])

    #print(definition_df)

    loop_through_definitions(definition_df, provinces_pixels, terrain_pixels, output_path)

    #print(find_dominant_terrain([159,135,248], provinces_pixels, terrain_pixels))
    

