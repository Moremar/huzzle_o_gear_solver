#!/usr/bin/env python3

# This program is a solver for the CAST O'GEAR puzzle from HUZZLE.
#
# It takes as input an initial position and a target position of the gear, each defined by :
#   - the side of the gear from 1 to 6 (see side numbering below)
#   - the tooth of the gear that is inside the cube from 0 to 4 (see teeth numbering below)
#   - the axis of the gear, either X, Y or Z (see axis direction below)
#   - the gear polarity, 1 or -1, indicating if the gear is facing its axis or not.
#
# It generates successive instructions to transition the gear from the initial to the target position.
#
# The cube sides are numbered from 1 to 6.
# We position the side with 2 notches at the top (side 1) and the side with an arrow mark on the right (side 5).
#
#             ___________       4 (back)
#            /    1     /|      5 (side with a small arrow mark at the bottom)
#           /_________/  |      6 (bottom, target side)
#          |         | 5 |
#    3 --> |    2    |  /
#          |_________|/
#
# We use the following axis to decide on the polarity :
#
#         Z|   / Y
#          |  /
#          | /
#          O ------- X
#
# The polarity of the gear is an indicator of which side of the gear is facing which direction.
# It is 1 when the side marked with HANAYAMA is facing its axis positive area, and -1 otherwise.
#
# The teeth of the gear need to be numbered from 0 to 4.
# When facing the side of the gear marked with HANAYAMA, we number as 0 the tooth with a hole, then 1
# the tooth on its left, then 2 the one on the left of tooth 1, and so on for 3 and 4.
#
# To solve the puzzle we must bring tooth 4 inside side 6 of the cube along axis X with polarity -1.


from collections import deque
import argparse

X, Y, Z = 'X', 'Y', 'Z'


# Dictionary listing all the possible moves from a position to another.
# Each position is represented by the side number (1 to 6) and the axis of the gear (X, Y or Z).
#
# (1, X) means that the gear is on side 1 of the cube and follows the X axis.
# A transition is represented as ((next_side, next_axis), tooth_incr, polarity_mult)
# A transition is either a rotation on the same side of the cube, or a move to an adjacent side of the cube.
#
# The tooth increment represents the change of the tooth inside the cube.
# It is 0 for in-place rotations, and either 1 or -1 when moving the gear from a side to another.
#
# The polarity multiplier indicates if the polarity of the gear changes due to a transition.
# It is -1 if the transition changes the polarity, and 1 if it doesn't.
TRANSITIONS = {
    (1, X) : { ((2, X), -1, 1), ((4, X),  1, 1), ((1, Y), 0, -1) },
    (1, Y) : { ((3, Y),  1, 1), ((1, X), 0, -1) },
    (2, X) : { ((1, X),  1, 1), ((2, Z), 0, -1) },
    (2, Z) : { ((5, Z), -1, 1), ((2, X), 0, -1) },
    (3, Y) : { ((1, Y), -1, 1), ((6, Y),  1, 1), ((3, Z), 0, 1) },
    (3, Z) : { ((4, Z),  1, 1), ((3, Y),  0, 1) },
    (4, Z) : { ((3, Z), -1, 1), ((5, Z),  1, 1), ((4, X), 0, 1) },
    (4, X) : { ((1, X), -1, 1), ((4, Z),  0, 1) },
    (5, Z) : { ((4, Z), -1, 1), ((2, Z),  1, 1), ((5, Y), 0, -1) },
    (5, Y) : { ((6, Y), -1, 1), ((5, Z),  0, -1) },
    (6, Y) : { ((5, Y),  1, 1), ((3, Y), -1, 1), ((6, X), 0, 1) },
    (6, X) : { ((6, Y),  0, 1) }
}


def solve(origin, target):
    """Find the shortest path to the target using a BFS"""
    to_process = deque([(origin, 0, [])])
    seen_states = {origin}
    while len(to_process) > 0:
        curr_state = to_process.popleft()
        (side_id, tooth, polarity), steps, path = curr_state
        if side_id not in TRANSITIONS:
            raise ValueError(f'{side_id} is an invalid initial position')
        for transition in TRANSITIONS[side_id]:
            (next_side_id, tooth_incr, polarity_mult) = transition
            next_polarity = polarity * polarity_mult
            next_tooth = (tooth + (tooth_incr * polarity)) % 5
            next_state = (next_side_id, next_tooth, next_polarity)
            if next_state in seen_states:
                # this state has already been checked before, skip it
                continue
            seen_states.add(next_state)
            next_path = path + [transition]
            if next_state == target:
                return next_path
            to_process.append((next_state, steps+1, next_path))

    raise ValueError('No solution found, check the provided initial and target positions')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-is', '--initial_side', type=int, default=1, choices=range(1, 7), help='Initial side of the cube')
    parser.add_argument('-ia', '--initial_axis', type=str, default='X', choices=['X', 'Y', 'Z'], help='Initial axis of the gear')
    parser.add_argument('-it', '--initial_tooth', type=int, default=0, choices=range(0, 5), help='Initial tooth inside the cube')
    parser.add_argument('-ip', '--initial_polarity', type=str, default='T', choices=['T', 'F'], help='Initial polarity of the gear, T if facing the axis, F otherwise')
    parser.add_argument('-ts', '--target_side', type=int, default=6, choices=range(1, 7), help='Initial side of the cube')
    parser.add_argument('-ta', '--target_axis', type=str, default='X', choices=['X', 'Y', 'Z'], help='Initial axis of the gear')
    parser.add_argument('-tt', '--target_tooth', type=int, default=4, choices=range(0, 5), help='Initial tooth inside the cube')
    parser.add_argument('-tp', '--target_polarity', type=str, default='F', choices=['T', 'F'], help='Initial polarity of the gear, T if facing the axis, F otherwise')

    args = parser.parse_args()
    origin = (args.initial_side, args.initial_axis), args.initial_tooth, 1 if args.initial_polarity == 'T' else -1
    target = (args.target_side, args.target_axis), args.target_tooth, 1 if args.target_polarity == 'T' else -1
    print(f'Origin : side {args.initial_side} axis {args.initial_axis} tooth {args.initial_tooth} polarity {args.initial_polarity}')
    print(f'Target : side {args.target_side} axis {args.target_axis} tooth {args.target_tooth} polarity {args.target_polarity}')
    return origin, target


if __name__ == '__main__':
    origin, target = parse_args()
    path = solve(origin, target)
    for (i, step) in enumerate(path):
        (side_id, axis), tooth_incr, polarity = step
        if tooth_incr == 0:
            print(f'Step {i + 1}: Rotate')
        else:
            print(f'Step {i + 1}: Move to side {side_id}')
