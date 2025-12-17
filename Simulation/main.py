import rclpy

from rclpy.executors import MultiThreadedExecutor
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

from modules.MultiNode import MultiNode
from modules.armMovement import init as amInit
from modules.lidar import init as lidarInit
from modules.movement import init as moveInit
from modules.navigator import init as navInit
from modules.objLocator import init as objInit
from modules.planner import init as planInit

def rosInit() -> None:
    rclpy.init(args=None)
    nodes: list[MultiNode] = [lidarInit(), objInit(), planInit(), amInit(), moveInit(), navInit()]

    executor = MultiThreadedExecutor()
    for node in nodes:
        executor.add_node(node)

    try:
        executor.spin()
    finally:
        for node in nodes:
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    rosInit()

    client = RemoteAPIClient()
    sim = client.require('sim')

    sim.setStepping(True)

    sim.startSimulation()
    while (t := sim.getSimulationTime()) < 3:
        print(f'Simulation time: {t:.2f} [s]')
        sim.step()
    sim.stopSimulation()
