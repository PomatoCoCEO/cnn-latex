from math import log2, ceil
FACTOR = 10


print("\\begin{tikzpicture}[x={(0.5pt,-0.5pt)},y={(0pt,1pt)},z={(1pt,0pt)},thick]")

layers = [
    (32,32,3),
    (16,16,32),
    (8,8,64),
    (8,8,128),
    (1,8192,1),
    (1,128,1),
    (1,10,1)
]

layer_phases = [
    [layers[0]],
    [layers[1]],
    [layers[2], layers[3]],
    layers[4:],
]


# first_layer_coords = (32,32,3)
# sec_layer_coords = (32,32,32)

# third_layer_coords = (16,16,32)
# fourth_layer_coords = (16,16,64)

# final_layer_coords = (8,8,64)

# layers = [first_layer_coords, sec_layer_coords, third_layer_coords, fourth_layer_coords, final_layer_coords]
init_z = 0
interval_layers_same = 5
interval_layers_diff = 40

z_tots = []
prev_z = init_z

proc_layer = lambda x: ceil(FACTOR * log2(x+1))

for i in range(len(layer_phases)):
    layers = layer_phases[i]
    for j in range(len(layers)):
        layer = layers[j]

        z = proc_layer(layer[2])
        z_tots.append(prev_z)
        if j == len(layers)-1:
            prev_z += interval_layers_diff + z
        else:
            prev_z += interval_layers_same + z
        # print("i,j,prev_z = %d,%d,%d" % (i,j,prev_z))
# z_poses = [l[2] for l in layers]
# z_poses[0] += init_z
# for i in range(1,len(z_poses)):
#     z_poses[i] = z_poses[i-1] + interval_layers_same + layers[i-1][2]
#  print(z_poses)

colours = ["red", "orange", "yellow", "green", "blue", "violet"]



k = len(z_tots)-1

prev_z = z_tots[-1]
thickness_fc = 5

drew_conv = False


for i in range(len(layer_phases)-1,-1,-1):
    for j in range(len(layer_phases[i])-1,-1,-1):
        layer = layer_phases[i][j]
        x = proc_layer(layer[0])
        y = proc_layer(layer[1])
        z = proc_layer(layer[2])

        if k != 0 and not drew_conv:
            # if i != len(layer_phases)-1 and j == len(layer_phases[i])-1:
            print("\\transline{%d}{%d}" % (z_tots[k-1], z_tots[k]))
        if k < len(z_tots)-1 and i != len(layer_phases)-1:
            # show dashed convolution with the next layer
            print("\\dashedconvol{%d}{%d}{%d}{%d}{%d}{%d}" % (-1.5, -1.5, z_tots[k]+z,3,3,z_tots[k+1]))
            drew_conv = True
        else:
            drew_conv = False
    

        if i == len(layer_phases)-1:
            # it is a classifying layer
            # args: x,y,z, cuboidHeight, thickness, realHeight, color
            print("\\fcblock{%.2f}{%.2f}{%d}{%d}{%d}{%d}{%s}" % (-thickness_fc/2,-y/2,z_tots[k],y,thickness_fc, layer[1], colours[k%len(colours)]))
        else:
            print("\\cnnblock{%.2f}{%.2f}{%d}{%d}{%d}{%d}{%s}{%d}" % (-x/2,-y/2,z_tots[k],x,y,z, colours[k%len(colours)], layer[2]))
            if j == 0:
                # annotate the layer
                print("\\annotatecnnx{%.2f}{%.2f}{%.2f}{%d}{%d}{%s}" %(-x/2, -y/2, z_tots[k], x, layer[0], colours[k%len(colours)]))
                print("\\annotatecnny{%.2f}{%.2f}{%.2f}{%d}{%d}{%s}" %(-x/2, -y/2, z_tots[k], y, layer[1], colours[k%len(colours)]))
        
        
        k -= 1

print("\\end{tikzpicture}")