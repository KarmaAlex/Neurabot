from rclpy.node import Node
from std_msgs.msg import String
class MultiNode(Node):
    def __init__(self, name:str, publishers:list[str], subscribers:list[str]):
        super().__init__(name)
        self._publishers = []
        self._subscribers = []
        for channel in publishers:
            self._publishers.append(self.create_publisher(String, channel, 10))
        for channel in subscribers:
            self._subscribers.append(self.create_subscription(String, channel, self.callback, 10))
        
    def callback(self, msg):
        pass