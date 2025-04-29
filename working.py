import os
import copy
from PIL import Image, ImageDraw, ImageFont


def main(**kwargs):
    pass
    width = kwargs.get('width', 0)
    height = kwargs.get('height', 0)
    border_width = kwargs.get('border_width', 2)
    colors = kwargs.get('colors', [])
    circles = kwargs.get('circles', [])
    file_output = kwargs.get('file_output', 'output/working.png')
    #create output directory
    if not os.path.exists('output'):
        os.makedirs('output')


    print(f"making: {file_output}")

    #make image
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)


    #calculate how many circles each pixel is inside
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

    #draw circles
    if True:
        for circle in circles:
            x, y, r = circle
            #transparent circle
            draw.ellipse((x - r, y - r, x + r, y + r), outline=(0, 0, 0), width=border_width)
            



    # save image
    if True:
        image.save(file_output)
    
    

    


if __name__ == '__main__':

    runs = 100

    for i in range(runs):
        kwargs = {}
        file_output = 'output/working_' + str(i) + '.png'
        kwargs['file_output'] = file_output
        



        
        width = 1000
        kwargs['width'] = width    
        height = 1000
        kwargs['height'] = height
        #circles
        if True:
            circles = []
            #circles.append((125, 125, 100))
            #circles.append((250, 125, 100))
            number_of_circles = i
            sizes = [25,50,100,200,400]
            multiple = 25
            import random
            for i in range(number_of_circles):
                #each circle is fully inside the canvas
                #each circle is a multiple of multiple ie 25, 50, 100, 200
                #each circle is on a grid of multiple
                r = random.choice(sizes)
                x = random.randint(r, width - r)
                #round to multiple
                x = int(x / multiple) * multiple
                y = random.randint(r, height - r)
                #round to multiple
                y = int(y / multiple) * multiple
                circles.append((x, y, r))
            kwargs['circles'] = circles
        #colors
        if True:
            colors = []
            if True:
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
            if False:
                colors.append([255, 0, 0])    # Red
                colors.append([245, 0, 17])
                colors.append([235, 0, 34])
                colors.append([225, 0, 51])
                colors.append([215, 0, 68])
                colors.append([205, 0, 85])
                colors.append([195, 0, 102])
                colors.append([185, 0, 119])
                colors.append([175, 0, 136])
                colors.append([165, 0, 153])
                colors.append([155, 0, 170])
                colors.append([150, 0, 172])
                colors.append([145, 0, 174])
                colors.append([137, 0, 176])
                colors.append([128, 0, 178])  # Purple-ish
            kwargs['colors'] = colors


        
        main(**kwargs)