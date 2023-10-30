import json
from math import ceil, log2

FACTOR_X = 10
FACTOR_Y = 10
FACTOR_Z = 5

FC_THICKNESS = 5

INTERVAL_BLOCKS = 40
INTERVAL_CNNS = 5
INTERVAL_FCS = 5


def load_data_json(filename):
    json_data = None
    with open(filename) as json_file:
        json_data = json.load(json_file)
    return json_data


def process_dimension(factor, dimension):
    return ceil(factor * log2(dimension))


# the only thing that is dependent on the disposition is the Z position, which should be decided
# at runtime
def print_cnn(cnn_layer, start_z, annotate: bool = False):
    # firstly create the cube shape for the CNN
    shape = cnn_layer["output_shape"]
    color = cnn_layer.get("color", "green")
    # create
    dx, dy, dz = shape[0], shape[1], shape[2]
    dx = process_dimension(FACTOR_X, dx)
    dy = process_dimension(FACTOR_Y, dy)
    dz = process_dimension(FACTOR_Z, dz)
    x = -dx / 2
    y = -dy / 2
    z = start_z
    print(
        "\cnnblock{%d}{%d}{%d}{%d}{%d}{%d}{%s}{%d}"
        % (x, y, z, dx, dy, dz, color, shape[2])
    )
    if annotate:
        # % arguments: x, y, z, deltaY, annotation, color
        print("\\annotatecnnx{%d}{%d}{%d}{%d}{%d}{%s}" % (x, y, z, dx, shape[0], color))
        print("\\annotatecnny{%d}{%d}{%d}{%d}{%d}{%s}" % (x, y, z, dy, shape[1], color))


def print_fc(fc_layer, start_z):
    out_shape = fc_layer["output_shape"]
    color = fc_layer.get("color", "blue")
    dy = process_dimension(FACTOR_Y, out_shape[0])
    thickness = FC_THICKNESS
    x = -thickness / 2
    y = -dy / 2
    z = start_z
    print(
        "\\fcblock{%d}{%d}{%d}{%d}{%d}{%d}{%s}"
        % (x, y, z, dy, thickness, out_shape[0], color)
    )


def print_maxpool(max_pool, start_z, end_z, input_shape):
    color = max_pool.get("color", "red")
    shape = max_pool["output_shape"]
    x1 = process_dimension(FACTOR_X, input_shape[0])
    y1 = process_dimension(FACTOR_Y, input_shape[1])
    z1 = start_z
    x2 = process_dimension(FACTOR_X, shape[0])
    y2 = process_dimension(FACTOR_Y, shape[1])
    z2 = end_z
    # args: x1, y1, z1, x2, y2, z2, color
    print("\\maxpool{%d}{%d}{%d}{%d}{%d}{%d}{%s}" % (x1, y1, z1, x2, y2, z2, color))


def print_layer_code(layer, start_z):
    layer_type = layer["type"]
    if layer_type == "conv":
        print_cnn(layer, start_z)
    elif layer_type == "input":
        print_cnn(layer, start_z, annotate=True)
    elif layer_type == "fc":
        print_fc(layer, start_z)
    elif layer_type == "maxpool":
        print_maxpool(layer, start_z, start_z + INTERVAL_BLOCKS, layer["input_shape"])
    else:
        raise Exception("Unknown layer type: " + layer_type)


def get_layer_zs(layers):
    zs = []
    curr_z = 0
    for i in range(len(layers)):
        layer = layers[i]
        layer_type = layer["type"]
        zs.append(curr_z)
        if layer_type == "conv" or layer_type == "input":
            z_cnn = process_dimension(FACTOR_Z, layer["output_shape"][2])
            curr_z += z_cnn
            if i < len(layers) - 1:
                next_layer = layers[i + 1]

                if next_layer["type"] == "conv":
                    # compare the shapes
                    x_next = next_layer["output_shape"][0]
                    y_next = next_layer["output_shape"][1]
                    x_curr = layer["output_shape"][0]
                    y_curr = layer["output_shape"][1]
                    if y_next == y_curr and x_next == x_curr:
                        curr_z += INTERVAL_CNNS
                    else:
                        curr_z += INTERVAL_BLOCKS
                elif next_layer["type"] == "fc":
                    curr_z += INTERVAL_BLOCKS
                    # interval 0
                elif next_layer["type"] == "maxpool":
                    # add the thickness
                    # pooling layer -> no interval
                    pass
        elif layer_type == "fc":
            curr_z += FC_THICKNESS
            curr_z += INTERVAL_FCS

        elif layer_type == "maxpool":
            curr_z += INTERVAL_BLOCKS
            # get the previous layer thickness
            # if i > 0:
            #     prev_layer = layers[i - 1]
            #     if prev_layer["type"] == "conv":
            #         curr_z += process_dimension(FACTOR_Z, prev_layer["output_shape"][2])
            #     else:
            #         raise Exception("Maxpool layer can only be preceded by a CNN layer")
        else:
            raise Exception("Unknown layer type: " + layer_type)
    return zs


def print_all_layers(layers, zs):
    for i in range(len(layers) - 1, -1, -1):
        layer = layers[i]
        layer_type = layer["type"]
        if layer_type == "maxpool":
            if i < len(layers) - 1:
                prev_layer = layers[i - 1]
                if prev_layer["type"] == "conv":
                    print_maxpool(layer, zs[i], zs[i + 1], prev_layer["output_shape"])
                else:
                    raise Exception("Maxpool layer can only be preceded by a CNN layer")
            else:
                raise Exception("Maxpool layer cannot be the first layer")
        # else:
        #     print_layer_code(layer, zs[i])
        elif layer_type == "conv":
            annotate = True
            if i > 0 and layers[i - 1]["type"] in ["conv", "input"]:
                annotate = False
            print_cnn(layer, zs[i], annotate)
        else:
            print_layer_code(layer, zs[i])


def build_nn_from_file(filename):
    json_data = load_data_json(filename)
    layers = json_data["architecture"]["layers"]
    zs = get_layer_zs(layers)
    print("\\begin{tikzpicture}[x={(0.5pt,-0.5pt)},y={(0pt,1pt)},z={(1pt,0pt)},thick]")
    print_all_layers(layers, zs)
    print("\end{tikzpicture}")
    # print(zs)


if __name__ == "__main__":
    build_nn_from_file("cnn.json")
