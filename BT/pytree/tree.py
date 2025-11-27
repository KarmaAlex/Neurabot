from typing import Any
import py_trees
from py_trees.common import Status
from random import random
import time

GOALS_LIST_KEY = "goals_list"
CURRENT_GOAL_KEY = "current_goal"
BATTERY_LEVEL_KEY= "battery_level"
MARKERS_LIST_KEY = "markers_list"
current_goal_id = 0
current_marker_id = 0

class Goal:
    def __init__(self, id:int, dist: float) -> None:
        self._distance:float = dist
        self._id = id

    def decreaseDist(self, amount:float) -> None:
        self._distance -= amount
    
    def getDistance(self) -> float: return self._distance

    def __repr__(self) -> str:
        return f"ID: {self._id}, Distance from goal: {self._distance}"
    
class Marker:
    def __init__(self, id:int, x:int, y:int) -> None:
        self._x = x
        self._y = y
        self._id = id
    
    def __repr__(self) -> str:
        return f"ID: {self._id} at x:{self._x}, y:{self._y}"

class ReadItem(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="ReadItem"):
        super(ReadItem, self).__init__(name)
        self._blackboard:py_trees.blackboard.Client = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=GOALS_LIST_KEY,
            access=py_trees.common.Access.WRITE
        )
        self._blackboard.register_key(
            key=CURRENT_GOAL_KEY,
            access=py_trees.common.Access.WRITE
        )
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("ReadItem setup")
        return super().setup(**kwargs)

    def update(self) -> Status:
        if len(list(self._blackboard.get(GOALS_LIST_KEY))) < 1:
            if(random() * 100 < 30):
                global current_goal_id
                current_goal_id += 1
                self._blackboard.set(GOALS_LIST_KEY, [Goal(current_goal_id, random() * 150 + 50)])
                return Status.FAILURE
        elif self._blackboard.get(CURRENT_GOAL_KEY) is None:
            goals:list[Goal] = self._blackboard.get(GOALS_LIST_KEY)
            self._blackboard.set(CURRENT_GOAL_KEY, goals[0])
            goals.remove(goals[0])
            self._blackboard.set(GOALS_LIST_KEY, goals)
        return Status.SUCCESS
            
class MoveToItem(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="MoveToItem"):
        super(MoveToItem, self).__init__(name)
        self._blackboard:py_trees.blackboard.Client = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=GOALS_LIST_KEY,
            access=py_trees.common.Access.WRITE
        )
        self._blackboard.register_key(
            key=CURRENT_GOAL_KEY,
            access=py_trees.common.Access.WRITE
        )
        self._blackboard.register_key(
            key=BATTERY_LEVEL_KEY,
            access=py_trees.common.Access.WRITE
        )
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("MoveToItem setup")
        return super().setup(**kwargs)

    def update(self) -> Status:
        curGoal:Goal = self._blackboard.get(CURRENT_GOAL_KEY)
        if curGoal is not None:
            move:float = random() * 30 + 10
            self._blackboard.set(BATTERY_LEVEL_KEY,
                                 self._blackboard.get(BATTERY_LEVEL_KEY) - move * 0.1)
            curGoal.decreaseDist(move)
            return Status.SUCCESS
        return Status.FAILURE

class BatteryOK(py_trees.behaviour.Behaviour):
    def __init__(self, minBat:float, name: str="BatteryOK"):
        super(BatteryOK, self).__init__(name)
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=BATTERY_LEVEL_KEY,
            access=py_trees.common.Access.READ
        )
        self._batThreshold:float = minBat

    def setup(self, **kwargs: Any) -> None:
        self.logger.info("BatteryOk setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if(self._blackboard.get(BATTERY_LEVEL_KEY) < self._batThreshold): return Status.FAILURE
        return Status.SUCCESS

class NotifyLowBattery(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="NotifyLowBattery"):
        super(NotifyLowBattery, self).__init__(name)
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=BATTERY_LEVEL_KEY,
            access=py_trees.common.Access.READ
        )
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("NotifyLowBattery setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        self.logger.error(f"Battery level low: {self._blackboard.get(BATTERY_LEVEL_KEY)}%")
        return Status.SUCCESS

class ReachedItem(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="ReachedItem"):
        super(ReachedItem, self).__init__(name)
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=CURRENT_GOAL_KEY,
            access=py_trees.common.Access.WRITE
        )
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("ReachedItem setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self._blackboard.get(CURRENT_GOAL_KEY).getDistance() > 0: return Status.FAILURE
        self._blackboard.set(CURRENT_GOAL_KEY, None)
        return Status.SUCCESS
    
class NotifyUser(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="NotifyUser"):
        super(NotifyUser, self).__init__(name)
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=CURRENT_GOAL_KEY,
            access=py_trees.common.Access.WRITE
        )

    def setup(self, **kwargs: Any) -> None:
        self.logger.info("NotifyUser setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        self.logger.info(f"Reached goal {self._blackboard.get(CURRENT_GOAL_KEY)}")
        self._blackboard.set(CURRENT_GOAL_KEY, None)
        return Status.SUCCESS
        
class WanderAction(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="WanderAction"):
        super(WanderAction, self).__init__(name)
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=BATTERY_LEVEL_KEY,
            access=py_trees.common.Access.WRITE
        )
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("WanderAction setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        move:float = random() * 50 + 10
        self._blackboard.set(BATTERY_LEVEL_KEY,
                             self._blackboard.get(BATTERY_LEVEL_KEY) - move * 0.1)
        return Status.SUCCESS
    
class FoundItem(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="FoundItem"):
        super(FoundItem, self).__init__(name)
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("FoundItem setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if(random() * 100 < 20): return Status.SUCCESS
        return Status.FAILURE
    
class AddMarker(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="AddMarker"):
        super(AddMarker, self).__init__(name)
        self._blackboard = self.attach_blackboard_client(name=self.name)
        self._blackboard.register_key(
            key=MARKERS_LIST_KEY,
            access=py_trees.common.Access.WRITE
        )
        
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("AddMarker setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        markers:list[Marker] = self._blackboard.get(MARKERS_LIST_KEY)
        global current_marker_id
        current_marker_id += 1
        markers.append(Marker(current_marker_id, int(random()*100), int(random()*100)))
        self._blackboard.set(MARKERS_LIST_KEY, markers)
        return Status.SUCCESS

def build_tree():
    foundSeq = py_trees.composites.Sequence("foundSequence", memory=False)
    foundSeq.add_children([ReachedItem(), NotifyUser()])
    failIsSucc = py_trees.decorators.FailureIsSuccess("failIsSuccess", foundSeq)
    findSeq = py_trees.composites.Sequence("FindSequence", memory=False)
    findSeq.add_children([ReadItem(), MoveToItem(), failIsSucc])
    findInverter = py_trees.decorators.Inverter("MainInverter", findSeq)
    mainSeq = py_trees.composites.Sequence("MainSequence", memory=False)
    wanderSeq = py_trees.composites.Sequence("WanderSequence", memory=False)
    wanderSeq.add_children([WanderAction(), FoundItem(), AddMarker()])
    batSeq = py_trees.composites.Sequence("BatterySequence", memory=False)
    batInverter = py_trees.decorators.Inverter("BatInverter", BatteryOK(15.0))
    batSeq.add_children([batInverter, NotifyLowBattery()])
    batSeqInverter = py_trees.decorators.Inverter("BatSequenceInverter", batSeq)
    mainSeq.add_children([batSeqInverter, findInverter, wanderSeq])
    repeat = py_trees.decorators.Repeat("Repeat", mainSeq, num_success=-1)
    root = py_trees.composites.Sequence("Root", memory=False)
    root.add_child(repeat)
    return root

def main(runs:int) -> None:
    root = build_tree()

    root.setup_with_descendants()

    blackboard = py_trees.blackboard.Client(name="Test")
    blackboard.register_key(
        key=GOALS_LIST_KEY,
        access=py_trees.common.Access.WRITE
    )
    blackboard.register_key(
        key=CURRENT_GOAL_KEY,
        access=py_trees.common.Access.WRITE
    )
    blackboard.register_key(
        key=BATTERY_LEVEL_KEY,
        access=py_trees.common.Access.WRITE
    )
    blackboard.register_key(
        key=MARKERS_LIST_KEY,
        access=py_trees.common.Access.WRITE
    )
    global current_goal_id
    current_goal_id+=1
    goals:list[Goal] = [Goal(current_goal_id, 39)]
    current_goal_id+=1
    goals.append(Goal(current_goal_id, 300))
    current_goal_id+=1
    goals.append(Goal(current_goal_id, 20))
    current_goal_id+=1
    goals.append(Goal(current_goal_id, 150))

    blackboard.set(GOALS_LIST_KEY, goals)
    blackboard.set(CURRENT_GOAL_KEY, None)
    blackboard.set(MARKERS_LIST_KEY, [])
    blackboard.set(BATTERY_LEVEL_KEY, 100.0)
    
    print("Behavior Tree Structure:")
    print(py_trees.display.unicode_tree(root, show_status=True))
    print()

    print(f"Running {runs} behavior tree ticks...")
    print("-" * 60)
    
    for i in range(runs):
        print(f"\n{'=' * 60}")
        print(f"Tick {i + 1}/{runs}")
        print(f"{'=' * 60}")
        
        print(f"Current goals: {blackboard.get(GOALS_LIST_KEY)}")
        print()

        print(f"Current goal: {blackboard.get(CURRENT_GOAL_KEY)}")
        print()

        print(f"Current markers: {blackboard.get(MARKERS_LIST_KEY)}")
        print()
        print(f"Current battery level: {blackboard.get(BATTERY_LEVEL_KEY)}")

        # Tick the tree
        root.tick_once()
        
        # Display the tree state
        print("\nTree State:")
        print(py_trees.display.unicode_tree(root, show_status=True))
        
        print(f"Final battery level: {blackboard.get(BATTERY_LEVEL_KEY)}%")
        print(f"Final goals: {blackboard.get(GOALS_LIST_KEY)}")
        print(f"Current goal: {blackboard.get(CURRENT_GOAL_KEY)}")
        print(f"Final markers: {blackboard.get(MARKERS_LIST_KEY)}")
        
        time.sleep(0.5)  # Small delay for readability

if __name__ == "__main__":
    main(50)