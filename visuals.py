from __future__ import annotations
import math
import neat
import pygame

from core import(
    W, H, PANEL_W, TRACK_W, MAX_SPD, NUM_RAYS,
    C_PANEL_BG, C_ACCENT, C_ACCENT2, C_ACCENT3, C_RED, C_WHITE, C_DIM,
    C_GRAPH_BG, C_GRID,
)
#nn viewer

INPUT_LABELS = []
for i in range(NUM_RAYS):
    INPUT_LABELS.append("R"+str(i))
OUTPUT_LABELS = ["STR", "ACC", "break"]

def draw_nn(surf, genome, config, x, y, w, h, font, inputs=None):

    panel = pygame.Surface((w,h), pygame.SRCALPHA)
    panel.fill((15, 15, 25, 210)) #color
    surf.blit(panel, (x, y))
    pygame.draw.rect(surf, C_ACCENT2, (x, y, w, h), 1, border_radius=5)

    title = font.render("Neural Network", True, C_WHITE)
    surf.blit(title, (x+5, y+3))

    if genome is None:
        return
    elif genome == None:
        return
    
    #turn the nodes into input, output and hide some
    input_keys = list(config.genome_config.input_keys)
    output_keys = list(config.genome_config.output_keys)
    hidden_keys = []

    for key in genome.nodes:
        if key not in input_keys and key not in output_keys:
            hidden_keys.append(key)

    #where each position should be 
    pad = 28
    area_x = x+pad
    area_y = y+20
    area_w = w-pad*2
    area_h = h-30

    positions = {}
    #inputs on the left side
    if i != 0:
        i = 0
    while i < len(input_keys):
        node_y = area_y + area_h * (i+0.5)/len(input_keys)
        positions[input_keys[i]] = (area_x, node_y)
        i = i+1

    if i != 0:
        i = 0
    
    #outputs on right
    while i <len(output_keys):
        node_y = area_y+area_h*(i+0.5)/ len(output_keys)
        positions[output_keys[i]] = (area_x + area_w, node_y)
        i = i+1
    
    if len(hidden_keys) > 0:
        cols = max(1, math.ceil(math.sqrt(len(hidden_keys))))
        rows = max(1, math.ceil(len(hidden_keys)/cols))
        i=0
        while i < len(hidden_keys):
            col = i%cols
            row = i//cols
            node_x = area_x + area_w * 0.3 + area_w*0.4*(col+0.5)/cols
            node_y = area_y + area_h * (row+0.5)/rows

            positions[hidden_keys[i]] = (node_x, node_y)
            i = i+1

        #draw connection lines
    for pair in genome.connections:
        src_key = pair[0]
        dst_key = pair[1]
        connection = genome.connections[pair]

        if not connection.enabled:
            continue
        
        if src_key not in positions or dst_key not in positions:
            continue
        
        weight = connection.weight

        if weight > 0:
            color = (60, 200, 100)
        else:
            color = (200, 60, 60)
        
        thickness = int(abs(weight))
        if thickness < 1:
            thickness = 1
        if thickness > 3:
            thickness = 3
        
        start_pos = positions[src_key]
        end_pos = positions[dst_key]
        pygame.draw.line(surf, color, (int(start_pos[0]), int(start_pos[1])), (int(end_pos[0]), int(end_pos[1])), thickness )

        # draw nodes
    
    try:
        for term in positions:
            node_x = int(positions[term][0])
            node_y= int(positions[term][1])

            if term in input_keys:
                index = input_keys.index(term)
                color = C_ACCENT2
                if index < len(INPUT_LABELS):
                    label = INPUT_LABELS[index]
                else:
                    label = str(term)
                #color if active and how strong the signal is 
                if inputs is not None and index < len(inputs):
                    sgnal = inputs[index]
                    color = (int(255 * (1 - sgnal)), int(255 * sgnal), 100) #ai helped with this line

            elif term in output_keys:
                index = output_keys.index(term)
                color = (255, 130, 100) #orangish
                if index < len(OUTPUT_LABELS):
                    label = OUTPUT_LABELS[index]
                else:
                    label = str(term)
            else:
                color = (200, 200, 100)
                label = str(term)
            pygame.draw.circle(surf, color, (node_x, node_y), 7)

            pygame.draw.circle(surf, (180, 180, 180), (node_x, node_y), 7, 1)
            label_img = font.render(label, True, C_WHITE)
            surf.blit(label_img, (node_x - label_img.get_width() // 2, node_y - 16))

    except:
        print("error with something")
        return



    #add stats