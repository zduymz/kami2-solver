from PIL import Image, ImageDraw
from point import Point, Group
import random
import numpy
import math
import sys
import os
from copy import deepcopy
sys.setrecursionlimit(10000)


def image_to_pixels(image_path):
    '''
        Get a numpy array of an image so that one can access values[x][y].
    '''
    image = Image.open(image_path, 'r')
    width, height = image.size
    pixel_values = list(image.getdata())
    if image.mode == 'RGB':
        channels = 3
    elif image.mode == 'L':
        channels = 1
    else:
        print("Unknown mode: %s" % image.mode)
        return None
    pixel_values = numpy.array(pixel_values).reshape((height, width, channels))
    return pixel_values


def is_the_same_color(c1, c2):
    for i in range(3):
        if int(math.fabs(c1[i] - c2[i])) >= 45:
            return False
    return True


def is_neighbor(c1, c2):
    count = 0
    for pc1 in c1.pos:
        for pc2 in c2.pos:
            if pc1 == pc2:
                count += 1
                break

    if count == 2:
        return True
    else:
        return False


def get_base_colors(pixel_values):
    base_colors = []
    r, g, b = pixel_values[-32][64 * 4 + 8]
    color = (r, g, b)
    base_colors.append(color)
    for i in range(64 * 4 + 8, 640, 8):
        r, b, g = pixel_values[-32][i]
        if not is_the_same_color(color, (r, b, g)):
            color = (r, b, g)
            base_colors.append(color)

    return base_colors


def set_group(c, value):
    if c.group != None:
        return
    else:
        c.group = value

    for n in c.neighbors:
        if c.color == n.color:
            set_group(n, value)


def load_image(image_path):
    # TODO: check image_path exist or not
    return image_to_pixels(image_path)


def prepare_graph_from_image(filename):
    T = create_point(640, 72 * 14)

    pixel_values = load_image(filename)
    base_colors = get_base_colors(pixel_values)
    # Setup color for each shell
    for v in T:
        x, y = v.pos_color
        r, g, b = pixel_values[y][x]
        v.color = (r, g, b)
        for color in base_colors:
            if is_the_same_color(color, (r, g, b)):
                v.color = color

    # Setup neighbors for each shell
    for i, v in enumerate(T):
        if i < 10:
            for x in range(len(T)):
                if is_neighbor(v, T[x]):
                    v.neighbors.append(T[x])
        elif i >= 280:
            for x in range(i - 11, 290, 1):
                if is_neighbor(v, T[x]):
                    v.neighbors.append(T[x])
        else:
            for x in range(i - 11, i + 11, 1):
                if is_neighbor(v, T[x]):
                    v.neighbors.append(T[x])

    # Setup group for each shell
    group_count = 0
    for v in T:
        set_group(v, group_count)
        group_count += 1

    # How many groups we have?
    groups = []
    tmp_groups = []
    for v in T:
        tmp_groups.append(v.group)
    tmp_groups = list(set(tmp_groups))
    for i in tmp_groups:
        groups.append(Group(i))

    for v in T:
        for g in groups:
            if v.group == g.id:
                g.points.append(v)
                break

    for g in groups:
        g.prepare_for_graph()

    return base_colors, groups


def get_node_from_nodeid(node_id, all_nodes):
    for node in all_nodes:
        if node.id == node_id:
            return node
    return None


def remove_node_from_nodeid(node_id, all_nodes):
    for node in all_nodes:
        if node.id == node_id:
            all_nodes.remove(node)
            break
    return all_nodes


def update_node_new_color(node_id, all_nodes, new_color):
    for node in all_nodes:
        if node.id == node_id:
            node.set_color(new_color)
            return all_nodes


def update_node_new_group_id(node_id, all_nodes, new_node_id):
    will_remove_node = get_node_from_nodeid(node_id, all_nodes)
    will_adding_node = get_node_from_nodeid(new_node_id, all_nodes)

    for node in all_nodes:
        if node.id == node_id or node.id == new_node_id:
            all_nodes.remove(node)

    for p in will_remove_node.points:
        will_adding_node.points.append(p)

    all_nodes.append(will_adding_node)

    return all_nodes


def merge_nodes(nodeA, nodeB):
    # update B neighbors to A neighbors
    A_neigbors = set(nodeA.neighbors)
    for n in nodeB.neighbors:
        if n == nodeA.id:
            continue
        A_neigbors.add(n)
    nodeA.neighbors = list(A_neigbors)
    # B's cells will be A's cells
    for p in nodeB.points:
        nodeA.points.append(p)
    return nodeA


def solver(node, new_color, all_nodes, base_colors, solution_path, maxAttempt):
    print 'start%s' % maxAttempt, node, node.color, '->', new_color, all_nodes

    # debug
    # if all_nodes.count(node) > 0:
    #     sys.exit(1)
    # something to make it stop
    if maxAttempt == 0:
        return False

    # update node a new color
    node.color = new_color
    # update neighbors
    for neighbor_id in node.neighbors:
        neighbor = get_node_from_nodeid(neighbor_id, all_nodes)
        if neighbor.color == new_color:
            node = merge_nodes(node, neighbor)
            solution_path[-1]['merge'].append(neighbor_id)
            all_nodes.remove(neighbor)

    if len(solution_path[-1]['merge']) == 0:
        return False

    all_nodes.insert(0, node)
    for old in solution_path[-1]['merge']:
        for x in all_nodes:
            x.replace_neighbor(old, node.id)

    # we stop when all_nodes = 1 (converge into a color)
    if len(all_nodes) == 1:
        print '[+] Found solution'
        print solution_path
        return solution_path

    # try every node with every color
    all_nodes = sort_group(all_nodes)
    for i_node in all_nodes:
        # for color in base_colors:
        for color in i_node.get_neighbors_color():
            solution_path_copy = solution_path[:]
            if i_node.color == color:
                continue
            info = {
                'node': i_node.id,
                'merge': [],
                'new_color': color
            }
            all_nodes_copy = deepcopy(all_nodes)
            all_nodes_copy.remove(
                get_node_from_nodeid(i_node.id, all_nodes_copy))
            solution_path_copy.append(info)
            next_node = deepcopy(i_node)
            result = solver(next_node, color, all_nodes_copy, base_colors, solution_path_copy,
                            maxAttempt=maxAttempt - 1)
            if result:
                return result


def start_solver(base_colors, all_nodes, number_of_moves):
    for node in all_nodes:
        for color in node.get_neighbors_color():
            solution_path = []
            if node.color == color:
                continue
            info = {
                'node': node.id,
                'merge': [],
                'new_color': color
            }
            all_nodes_copy = deepcopy(all_nodes)
            all_nodes_copy.remove(
                get_node_from_nodeid(node.id, all_nodes_copy))
            solution_path.append(info)
            next_node = deepcopy(node)
            result = solver(next_node, color, all_nodes_copy,
                            base_colors, solution_path, number_of_moves)
            if result:
                return result
        # print 'End', node


def create_point(width, height):
    T = []
    delta = 0.5
    for y in range(0, height + 1, 36):
        for x in range(0, width, 64):
            if y == 0:
                T.append(Point(x, x + 64, y, y + 36, is_first_row=True))
            elif y == height:
                T.append(Point(x, x + 64, y - 36, y,
                               is_last_row=True, delta=delta))
            else:
                T.append(Point(x, x + 64, y - 36, y + 36, delta=delta))
        delta += 0.5
    return T


def sort_group(all_groups):
    for i in xrange(len(all_groups)):
        cursor = all_groups[i]
        pos = i
        while pos > 0 and all_groups[pos - 1].weight() < cursor.weight():
            all_groups[pos] = all_groups[pos - 1]
            pos = pos - 1
        all_groups[pos] = cursor
    return all_groups


def draw_solution(step, all_groups):
    im = Image.new('RGB', (640, 72 * 14), 'gray')
    draw = ImageDraw.ImageDraw(im)
    draw = ImageDraw.Draw(im)
    for group in all_groups:
        for point in group.points:
            draw.polygon(point.pos, fill=(point.color))
    im.save('%s.jpg' % step)


def main():
    filename = sys.argv[1]
    number_of_moves = int(sys.argv[2])

    base_colors, all_nodes = prepare_graph_from_image(filename)
    all_nodes = sort_group(all_nodes)
    solution_path = start_solver(base_colors, all_nodes, number_of_moves)

    for count, step in enumerate(solution_path):
        all_nodes = update_node_new_color(
            step['node'], all_nodes, step['new_color'])
        for group_id in step['merge']:
            all_nodes = update_node_new_group_id(
                group_id, all_nodes, step['node'])

        draw_solution(count + 1, all_nodes)


if __name__ == '__main__':
    main()
