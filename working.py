import os
import copy
from PIL import Image, ImageDraw, ImageFont
import time


alphabet_brail = {}
alphabet_brail['a'] = [[True, False],
                       [False, False],
                       [False, False]]
#c
alphabet_brail['c'] = [[True, True],
                       [False, False],
                       [False, False]]
#e
alphabet_brail['e'] = [[True, False],
                       [False, True],
                       [False, False]]
alphabet_brail['j'] = [[False, True],
                          [True, True],                          
                          [False, False]]
#l
alphabet_brail['l'] = [[True, False],
                       [True, False],
                       [True, False]]
#n
alphabet_brail['n'] = [[True, True],
                          [False, True],
                          [True, False]]
alphabet_brail["o"] = [[True, False],
                       [False, True],
                       [True, False]]
#r
alphabet_brail['r'] = [[True, False],
                          [True, True],
                          [True, False]]
#w
alphabet_brail['w'] = [[False, True],
                       [True, True],
                       [False, True]]
alphabet_brail['y'] = [[True, True],
                        [False, True],
                        [True, True]]


                       
alphabet_morse = {}
#a
alphabet_morse['a'] = ["dot","dash"]
#c
alphabet_morse['c'] = ["dash","dot","dash","dot"]
#e
alphabet_morse['e'] = ["dot"]
alphabet_morse['j'] = ["dot","dash","dash","dash"]                      
#l
alphabet_morse['l'] = ["dot","dash","dot","dot"]
#n
alphabet_morse['n'] = ["dash","dot"]
alphabet_morse['o'] = ["dash","dash","dash"]
#r
alphabet_morse['r'] = ["dot","dash","dot"]
#w

alphabet_morse['w'] = ["dot","dash","dash"]
alphabet_morse['y'] = ["dash","dot","dash","dash"]

def main(**kwargs):
    pass
    data = kwargs.get('data', "")
    width = kwargs.get('width', 0)
    height = kwargs.get('height', 0)
    border_width = kwargs.get('border_width', 2)
    colors = kwargs.get('colors', [])
    circles = kwargs.get('circles', [])
    file_output = kwargs.get('file_output', 'output/working.png')
    color_background = kwargs.get('color_background', [255, 255, 255])
    color_background_tuple = tuple(color_background)
    #create output directory for full file_output
    output_dir = os.path.dirname(file_output)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_time = time.time()
    print(f"making: {file_output}")

    overwrite = kwargs.get('overwrite', True)

    #make image
    image = Image.new('RGB', (width, height), color_background_tuple)
    draw = ImageDraw.Draw(image)


    #only make if file_output doesnt exist or overwrite is True
    if not os.path.exists(file_output) or overwrite:
        
        

        #calculate how many circles each pixel is inside
        old = False
        if old:
            for x in range(width):
                for y in range(height):
                    count = 0
                    for circle in circles:
                        cx, cy, r = circle
                        if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                            count += 1
                    #set color based on count
                    if count > 0:
                        #print(count)
                        color = colors[count % len(colors)]
                        draw.point((x, y), fill=tuple(color))
        else:
            import numpy as np

            # Create a grid of coordinates
            x_coords, y_coords = np.meshgrid(range(width), range(height))
            count_matrix = np.zeros((height, width), dtype=int)

            # Calculate how many circles each pixel is inside
            for cx, cy, r in circles:
                mask = (x_coords - cx) ** 2 + (y_coords - cy) ** 2 <= r ** 2
                count_matrix += mask

            # Set color based on count
            for count in np.unique(count_matrix):
                if count > 0:
                    color = colors[count % len(colors)]
                    mask = count_matrix == count
                    for y, x in zip(*np.where(mask)):
                        draw.point((x, y), fill=tuple(color))
        #draw circles
        if True:
            for circle in circles:
                x, y, r = circle
                #transparent circle
                draw.ellipse((x - r, y - r, x + r, y + r), outline=(0, 0, 0), width=border_width)
                



        # save image
        if True:
            image.save(file_output)
        
        #time in hour:minute
        time_taken_string = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))

        print(f"Time taken: {time_taken_string}")

    else:
        print(f"File already exists: {file_output}")
        return


Image.MAX_IMAGE_PIXELS = None  # Set to None to disable the warning entirely

def make_animation(**kwargs):
    #make a gif scaled to 1000x1000 and save as gif and avi
    folder = kwargs.get('folder', 'output')
    size = kwargs.get('size', 1000)
    duration = kwargs.get('duration', 250)
    file_output_gif = f"{folder}/working.gif"
    if True:
        #make gif
        images = []
        for i in range(2000):
            #file_input = f"{folder}/working_{i}/working.png"
            file_input = f"{folder}/working_{i}.png"
            if os.path.exists(file_input):
                image = Image.open(file_input)
                #resize to 1000 by height
                image = image.resize((size, int(size * image.height / image.width)), Image.ANTIALIAS)
                images.append(image)
                print(".", end='', flush=True)
            else:
                break
        images[0].save(file_output_gif, save_all=True, append_images=images[1:], duration=duration, loop=0)
        
import random    
 ###########################################################
#get circles
def get_circles_data(**kwargs):
    circles = []

    width = kwargs.get('width', 0)
    height = kwargs.get('height', 0)

    diameter = 50
    diameter = 52
    #base = int(width * 0.05)
    #diameter = int(base + (0.0004 * width))
    kwargs["diameter"] = diameter
    spacing = 100
    spacing_letter = 240
    #spacing = base* 4
    #kwargs["spacing"] = spacing
    expansion = 1.6
    kwargs["expansion"] = expansion

    start_shift_x = 500
    start_shift_y = 500
    shift_x = 0
    shift_y = 0
    current_x = start_shift_x
    current_y = start_shift_y

    index = 0
    data = kwargs.get('data', "")
    #for each letter in data
    
    for letter in data:        
        wid = 2
        hei = 3
        letter_brail = alphabet_brail[letter]
        letter_morse = alphabet_morse[letter]
        for x_count in range(wid):
            for y_count in range(hei):
                dia_current = kwargs['diameter']
                current_dot_state = letter_brail[y_count][x_count]
                if current_dot_state:

                    start_dia = diameter
                    if letter_morse[0] == "dash":
                        start_dia = diameter * 1.6
                    dia_current = start_dia
                    for i in range(len(letter_morse)):
                        dot_x = current_x + (x_count * spacing)
                        dot_y = current_y + (y_count * spacing)
                        rad = dia_current / 2
                        circle = (dot_x, dot_y, rad)
                        
                        circles.append(circle)                  
                        
                        if i != len(letter_morse) - 1:
                            current = letter_morse[i+1]
                            #expand if its a dash and not the first
                            if current == "dot":
                                dia_current = diameter + diameter
                            elif current == "dash":
                                dia_current = dia_current * 2 #+ int(diameter * expansion)
                        pass
        current_x += spacing_letter
        current_y += 0
        

    return circles




def get_circle_random(**kwargs):
    if True:            
        #circles.append((125, 125, 100))
        #circles.append((250, 125, 100))
        #number_of_circles = i
        sizes_base = [width*0.4,width*0.2, width*0.1, width*0.05, width*0.025, width*0.0125,]#, width*0.8]
        sizes_dist = []
        #populate an array so the smaller sizes are proprtionally more likely to be chossen
        for i in range(len(sizes_base)):
            for j in range(i*4):
                sizes_dist.append(sizes_base[i])

        sizes = sizes_dist

        #turn all sizes into int
        sizes = [int(x) for x in sizes]
        multiple = 25
        
        #for i in range(number_of_circles):

        if True:
            #each circle is fully inside the canvas
            #each circle is a multiple of multiple ie 25, 50, 100, 200
            #each circle is on a grid of multiple
            r = random.choice(sizes)
            success = False
            while not success:
                try:
                    x = random.randint(r, width - r)
                    #round to multiple
                    x = int(x / multiple) * multiple
                    y = random.randint(r, height - r)
                    #round to multiple
                    y = int(y / multiple) * multiple
                    success = True
                except:
                    print(f"bad guess trying again")
            
            circles.append((x, y, r))
    return circles


def get_colours(**kwargs):
    color_style = kwargs.get('color_style', 'rainbow')
    if False:
        colors.append([255, 99, 71])    # Tomato
        colors.append([135, 206, 250])  # Light Sky Blue
        colors.append([144, 238, 144])  # Light Green
        colors.append([255, 182, 193])  # Light Pink
        colors.append([255, 255, 102])  # Light Yellow
        colors.append([173, 216, 230])  # Light Blue
        colors.append([255, 160, 122])  # Light Salmon
        colors.append([221, 160, 221])  # Plum
        colors.append([240, 230, 140])  # Khaki
        colors.append([152, 251, 152])  # Pale Green
    #rinabow
    if color_style == "rainbow":
        #20 steps
        if False:
            colors = [
                        [255, 0, 0],     # Red
                        [255, 32, 0],
                        [255, 64, 0],
                        [255, 96, 0],
                        [255, 128, 0],   # Orange
                        [255, 160, 0],
                        [255, 192, 0],
                        [255, 224, 0],
                        [192, 255, 0],   # Yellow-green
                        [128, 255, 0],
                        [64, 255, 64],   # Greenish
                        [0, 255, 128],
                        [0, 224, 192],   # Cyan-turquoise
                        [0, 160, 255],   # Light blue
                        [0, 96, 255],    # Blue
                        [64, 0, 255],    # Indigo
                        [128, 0, 224],
                        [160, 0, 192],
                        [192, 0, 160],
                        [224, 0, 128],   # Purple
                    ]
        #10 steps
        if True:
            #basic
            if False:
                colors = [
                            [255, 0, 0],     # Red
                            [255, 64, 0],    # Red-orange
                            [255, 128, 0],   # Orange
                            [255, 192, 0],   # Yellow-orange
                            [192, 255, 0],   # Yellow-green
                            [0, 255, 64],    # Green
                            [0, 192, 192],   # Cyan
                            [0, 128, 255],   # Blue
                            [64, 0, 255],    # Indigo
                            [128, 0, 128],   # Purple
                        ]
            #trendy
            if True:
                #dark
                if True:
                    colors = [
                                [153, 27, 27],    # Brick Red
                                [179, 74, 21],    # Burnt Orange
                                [191, 111, 36],   # Ochre
                                [169, 134, 54],   # Earthy Yellow
                                [112, 128, 40],   # Olive Green
                                [69, 120, 98],    # Sage/Muted Teal
                                [58, 99, 129],    # Dusty Blue
                                [72, 61, 139],    # Indigo
                                [92, 52, 102],    # Eggplant
                                [119, 33, 111],   # Deep Plum
                            ]
                #bright
                if False:
                    colors = [
                                [200, 55, 55],     # Warm Red Clay
                                [220, 100, 40],    # Rusty Orange
                                [230, 150, 60],    # Golden Saffron
                                [210, 180, 70],    # Earthy Yellow
                                [150, 160, 70],    # Moss Green
                                [90, 150, 120],    # Dusty Jade
                                [80, 135, 160],    # Ocean Blue
                                [100, 100, 180],   # Washed Indigo
                                [130, 80, 150],    # Orchid Violet
                                [160, 60, 130],    # Bright Plum
                            ]
    #lawrence
    if color_style == "lawrence":
        teal_blue = [12,127,154]
        yellow = [224,196,34]
        cyan_blue = [60,168,194]
        purple = [127,60,104]
        #repeat yellow,cyan blue, purple
        colors = [
                    yellow,
                    yellow,
                    cyan_blue,
                    purple,
                    yellow,
                    cyan_blue,
                    purple,
                    yellow,
                    cyan_blue,  
                    purple,
                    yellow,
                    cyan_blue,
                    purple,
                    yellow,
                    cyan_blue,
                    purple

                ]
    if color_style == "none":
        colors = [[255, 255, 255]]
    return colors

if __name__ == '__main__':

    #mode = "random"
    mode = "data"

    #make the random the same everytime it's run
    random.seed(0)

    runs = 300
    #runs = 1

    kwargs = {}
    width = 2000
    kwargs['width'] = width    
    height = 2000
    kwargs['height'] = height
    #circles
    border_width = int(width / 1000)
    kwargs['border_width'] = border_width
    color_background =  [12,127,154]       
    #color_background =  [255,255,255]       
    kwargs['color_background'] = color_background

    circles = []

    if mode == "data":
        #data = "j"
        #data = "o"
        #data = "y"
        data = "joy"
        #data = "lawrence"
        kwargs['data'] = data
        circles = get_circles_data(**kwargs)
        data_no_spaces = data.replace(" ", "_")
        folder_output = f"output/{width}_{data_no_spaces}_data"

    if mode == "random":
        for i in range(runs):
            circles.append(get_circle_random(**kwargs))
        folder_output = f"output/{width}_random"

    
    
    
    animate = True
    if animate:
        start = 0
    else:
        start = len(circles) - 1
    
    for i in range(start, len(circles)):        
        

        #add first i circles to kwargs as "circles"
        kwargs['circles'] = circles[:i+1]

        #file_output = f"output/{width}_{data_no_spaces}_random/working_{i}/working.png"
        file_output = f"{folder_output}/working_{i}.png"
        

        kwargs['file_output'] = file_output
        folder = os.path.dirname(file_output)
        if not os.path.exists(folder):
            os.makedirs(folder)
        kwargs['folder'] = folder
        


        
        
        

        
        #colors
        if True:
            #color_style = "lawrence"
            #color_style = "none"
            color_style = "rainbow"
            kwargs['color_style'] = color_style
            colors = get_colours(**kwargs)            
            kwargs['colors'] = colors


        
        main(**kwargs)

    import yaml
    #save kwargs to yaml file
    file_output = f"{folder_output}/kwargs.yaml"
    with open(file_output, 'w') as file:
        yaml.dump(kwargs, file)
    #save circles to yaml file
    file_output = f"{folder_output}/circles.yaml"
    with open(file_output, 'w') as file:
        yaml.dump(circles, file)

    #make animation
    kwargs["folder"] = folder_output
    kwargs["duration"] = 1000
    make_animation(**kwargs)