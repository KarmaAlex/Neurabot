from typing import Any
import py_trees
from py_trees.common import Status
from random import random
import time

GOALS_LIST_KEY = "goals_list"
CURRENT_GOAL_KEY = "current_goal"

class Goal:
    def __init__(self, dist: float=0.0) -> None:
        self._distance:float = dist

    def decreaseDist(self, amount:float) -> None:
        self._distance -= amount
    
    def getDistance(self) -> float: return self._distance

    def __repr__(self) -> str:
        return f"Distance from goal: {self._distance}"

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
                self._blackboard.set(GOALS_LIST_KEY, [Goal(random() * 150 + 50)])
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
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("MoveToItem setup")
        return super().setup(**kwargs)

    def update(self) -> Status:
        curGoal = self._blackboard.get(CURRENT_GOAL_KEY)
        if curGoal is not None:
            curGoal.decreaseDist(random() * 30 + 10)
            return Status.SUCCESS
        return Status.FAILURE
        
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

class CloseGrip(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="CloseGrip"):
        super(CloseGrip, self).__init__(name)
        
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("CloseGrip setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        return Status.SUCCESS
    
class MoveHome(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="MoveHome"):
        super(MoveHome, self).__init__(name)

    def setup(self, **kwargs: Any) -> None:
        self.logger.info("MoveHome setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        return Status.SUCCESS
    
class OpenGrip(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="OpenGrip"):
        super().__init__(name)

    def setup(self, **kwargs: Any) -> None:
        self.logger.info("OpenGrip setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        return Status.SUCCESS
    
class WanderAction(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="WanderAction"):
        super(WanderAction, self).__init__(name)
    
    def setup(self, **kwargs: Any) -> None:
        self.logger.info("WanderAction setup")
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        return Status.SUCCESS

def build_tree():
    foundSeq = py_trees.composites.Sequence("foundSequence", memory=False)
    foundSeq.add_children([ReachedItem(), CloseGrip(), MoveHome(), OpenGrip()])
    failIsSucc = py_trees.decorators.FailureIsSuccess("failIsSuccess", foundSeq)
    findSeq = py_trees.composites.Sequence("FindSequence", memory=False)
    findSeq.add_children([ReadItem(), MoveToItem(), failIsSucc])
    inverter = py_trees.decorators.Inverter("Inverter", findSeq)
    mainSeq = py_trees.composites.Selector("MainSequence", memory=False)
    mainSeq.add_children([inverter, WanderAction()])
    repeat = py_trees.decorators.Repeat("Repeat", mainSeq, num_success=50)
    root = py_trees.composites.Sequence("Root", memory=False)
    root.add_child(repeat)
    return root

def main(runs: int) -> None:
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

    blackboard.set(GOALS_LIST_KEY, [Goal(39), Goal(300), Goal(20), Goal(150)])
    blackboard.set(CURRENT_GOAL_KEY, None)
    
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

        # Tick the tree
        root.tick_once()
        
        # Display the tree state
        print("\nTree State:")
        print(py_trees.display.unicode_tree(root, show_status=True))
        
        # Show final battery level
        print(f"Final goals: {blackboard.get(GOALS_LIST_KEY)}")
        print(f"Current goal: {blackboard.get(CURRENT_GOAL_KEY)}")
        
        time.sleep(0.5)  # Small delay for readability

if __name__ == "__main__":
    main(50)