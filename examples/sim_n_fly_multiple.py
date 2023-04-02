import argparse
import os
from signal import SIGINT, signal

import numpy as np
from PyFlyt.crazyflie import Simulator, SwarmController


def shutdown_handler(*_):
    print("ctrl-c invoked")
    os._exit(1)


def get_args():
    parser = argparse.ArgumentParser(description="Fly a single Crazyflie in a circle.")

    parser.add_argument(
        "--simulate",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="Simulate the circle.",
    )

    parser.add_argument(
        "--hardware",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="Run the circle on an actual drone.",
    )

    return parser.parse_args()


def fake_handler():
    start_pos = np.array(
        [[0.0, -1.0, 0.05], [0.0, 1.0, 0.05], [-1.0, 0.0, 0.05], [1.0, 0.0, 0.05]]
    )
    start_orn = np.array(
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    )

    # spawn in a drone
    UAVs = Simulator(start_pos=start_pos, start_orn=start_orn)
    UAVs.set_pos_control(True)

    return UAVs


def real_handler():
    URIs = []
    URIs.append("radio://0/10/2M/E7E7E7E7E2")
    URIs.append("radio://0/10/2M/E7E7E7E7E7")
    URIs.append("radio://0/30/2M/E7E7E7E7E0")
    URIs.append("radio://0/10/2M/E7E7E7E7E6")

    # connect to a drone
    UAVs = SwarmController(URIs)
    UAVs.set_pos_control(True)

    # reshuffle to optimal positions
    start_pos = np.array(
        [[0.0, -1.0, 0.05], [0.0, 1.0, 0.05], [-1.0, 0.0, 0.05], [1.0, 0.0, 0.05]]
    )
    start_orn = np.array(
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    )
    UAVs.reshuffle(start_pos, start_orn)

    return UAVs


if __name__ == "__main__":
    args = get_args()
    signal(SIGINT, shutdown_handler)

    UAVs = None
    if args.simulate:
        UAVs = fake_handler()
    elif args.hardware:
        UAVs = real_handler()
    else:
        print("Guess this is life now.")
        exit()

    # arm all drones
    UAVs.arm([1] * UAVs.num_drones)

    # initial hover
    UAVs.set_setpoints(
        np.array(
            [
                [0.0, -1.0, 1.0, 0.0],
                [0.0, 1.0, 1.0, 0.0],
                [-1.0, 0.0, 1.0, 0.0],
                [1.0, 0.0, 1.0, 0.0],
            ]
        )
    )
    UAVs.sleep(10)

    # send the drone back down
    UAVs.set_setpoints(
        np.array(
            [
                [0.0, -1.0, -1.0, 0.0],
                [0.0, 1.0, -1.0, 0.0],
                [-1.0, 0.0, -1.0, 0.0],
                [1.0, 0.0, -1.0, 0.0],
            ]
        )
    )
    UAVs.sleep(5)

    # stop the drone flight controller
    UAVs.arm([0] * UAVs.num_drones)
    UAVs.sleep(5)

    # end the drone control
    UAVs.end()
