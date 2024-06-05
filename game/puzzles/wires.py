import random
from puzzles import Puzzle

wire_cut = [False] * 6
wires = []
rand_num = -1

correct_wire = -1

COLORS = ['r', 'y', 'b', 'g', 'w', 'o', 'k']  # Example colors: red, yellow, blue, green, white, orange, black

def __get_correct_wire(wires, L):
    # Count the number of each color of wire
    yellow_count = wires.count('y')
    white_count = wires.count('w')
    red_count = wires.count('r')

    # Decision logic to determine which wire to cut based on the given conditions
    if yellow_count == 0 and L % 2 != 0:
        return 3  # Cut the third wire
    elif yellow_count == 1 and white_count > 1:
        return 4  # Cut the fourth wire
    elif red_count == 0:
        return 6  # Cut the last wire
    else:
        return 4  # Otherwise, cut the fourth wire
    
def init(app):
    global material_dict 
    materials = app.bomb.findAllMaterials('wire.*')
    material_dict = {
        'r': materials.findMaterial('wire.red'),
        'g': materials.findMaterial('wire.green'),
        'y': materials.findMaterial('wire.yellow'),
        'b': materials.findMaterial('wire.blue'),
        'w': materials.findMaterial('wire.white'),
        'o': materials.findMaterial('wire.orange'),
        'k': materials.findMaterial('wire.black')
    }


def generate_puzzle(app):
    global wire_cut
    global correct_wire
    wires = random.choices(COLORS, k=6)
    rand_num = random.randint(1, 9)
    correct_wire = __get_correct_wire(wires, rand_num)
    print(correct_wire)

    app.num_texts[int(Puzzle.WIRES)].setText(str(rand_num).zfill(2))

    for i in range(6):
        top_np = app.bomb.find(f'**/wire{i}.top')
        bot_np = app.bomb.find(f'**/wire{i}.bottom')

        wire_color = wires[i]
        material = material_dict[wire_color]
        top_np.setMaterial(material, 1)
        bot_np.setMaterial(material, 1)

        _, p, r = top_np.getHpr()
        top_np.setHpr(91.78852081298828, p, r)
    
    wire_cut = [False] * 6

def focus(app):
    app.bomb.hprInterval(0.25, (90, 0, 0)).start()
    app.focused = Puzzle.WIRES

def __set_wire_hpr(wire_np, direction):
    h, p, r = wire_np.getHpr()
    angle = random.randint(18, 25)
    wire_np.setHpr(h + direction * angle, p, r)

def cut_wire(app, wire_idx):
    if not wire_cut[wire_idx - 1]:
        direction = 1 if random.random() < 0.5 else -1
        wire_top_np = app.bomb.find(f'**/wire{wire_idx - 1}.top')
        __set_wire_hpr(wire_top_np, direction)
        wire_cut[wire_idx - 1] = True
        if wire_idx != correct_wire:
            app.handle_mistake()
        else:
            app.solve_puzzle(Puzzle.WIRES)
