from MultiNode import MultiNode
import rclpy

from rclpy.executors import MultiThreadedExecutor

from armMovement import init as amInit
from lidar import init as lidarInit
from movement import init as moveInit
from navigator import init as navInit
from objLocator import init as objInit
from planner import init as planInit

if __name__ == '__main__':
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