## Real world
```mermaid
graph TD
    Root["→<br/>Sequence"]
    
    Repeat{δ<br/>Repeat}
    SeqGoal[→<br/>Sequence]
    
    Blackboard["Blackboard"]

    Inverter{δ<br/>Inverter}
    GetGoal["Read next item<br/>Action"]
    NotifyUser["Notify user<br/>Action"]

    GoalReachedSeq["→<br/>Sequence"]
    FailIsSucc{δ<br/>Failure is <br/>success}
    GoalReached(["Reached item<br/>Condition"])
    BatSeqInvert{"δ<br/>Inverter"}
    BatteryCheck(["Battery OK<br/>Condition"])
    BatSequence["→<br/>Sequence"]
    BatNotify["Notify low<br/>battery<br/>Action"]
    BatInverter{"δ<br/>Inverter"}
    WanderSeq["→<br/>Sequence"]
    FoundItem(["Found item<br/>Condition"])
    AddMark["Add marker<br/>on map<br/>Action"]

    WanderTask["Wander<br/>Action"]

    SeqTask["→<br/>Sequence"]
    MoveToObj["Move to item<br/>Action"]
    
    Root --> Repeat
    
    Repeat --> SeqGoal
    SeqGoal --> BatSeqInvert
    BatSeqInvert --> BatSequence
    BatSequence --> BatInverter
    BatInverter --> BatteryCheck
    BatteryCheck --> |Read|Blackboard
    BatSequence --> BatNotify
    
    SeqGoal --> Inverter
    SeqGoal --> WanderSeq
    WanderSeq --> WanderTask
    WanderSeq --> FoundItem
    WanderSeq --> AddMark
    AddMark --> |Write|Blackboard
    Inverter --> SeqTask
    
    SeqTask --> GetGoal
    GetGoal --> |Read|Blackboard
    SeqTask --> MoveToObj
    MoveToObj -->|Read/Write|Blackboard
    SeqTask --> FailIsSucc
    FailIsSucc --> GoalReachedSeq
    GoalReachedSeq --> GoalReached
    GoalReached -->|Read|Blackboard
    GoalReachedSeq --> NotifyUser

    WanderTask -->|Write|Blackboard

    style Root fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style SeqGoal fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style GoalReached fill:#e8f5e9,stroke:#333,stroke-width:2px,color:#000
    style GetGoal fill:#f3e5f5,stroke:#333,stroke-width:2px,color:#000
    style SeqTask fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style GoalReachedSeq fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style MoveToObj fill:#f3e5f5,stroke:#333,stroke-width:2px,color:#000
    style WanderTask fill:#f3e5f5,stroke:#333,stroke-width:2px,color:#000
    style Blackboard fill:#000000,stroke:#333,stroke-width:2px,color:#fff
    style Inverter fill:#f8c2d4,stroke#333,stroke-width:2px,color:#000
    style Repeat fill:#f8c2d4,stroke#333,stroke-width:2px,color:#000
    style FailIsSucc fill:#f8c2d4,stroke#333,stroke-width:2px,color:#000
    style BatSeqInvert fill:#f8c2d4,stroke#333,stroke-width:2px,color:#000
    style BatInverter fill:#f8c2d4,stroke#333,stroke-width:2px,color:#000
    style BatSequence fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style WanderSeq fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style BatteryCheck fill:#e8f5e9,stroke:#333,stroke-width:2px,color:#000
    style FoundItem fill:#e8f5e9,stroke:#333,stroke-width:2px,color:#000
    style BatNotify fill:#f3e5f5,stroke:#333,stroke-width:2px,color:#000
    style AddMark fill:#f3e5f5,stroke:#333,stroke-width:2px,color:#000
    style NotifyUser fill:#f3e5f5,stroke:#333,stroke-width:2px,color:#000
```
## Simulation Behavioural Tree Node Description

### Control Nodes

- **Root Sequence (→)**: Main sequence node that executes children from left to right. Succeeds if all children succeed.
- **Repeat(δ)**: Repeatedly executes child sequence
- **SeqGoal (→)**: Sequence node that executes the main task workflow.
- **BatSeqInvert(δ)**: Interrupts the workflow if the robot doesn't have enough power
- **BatSequence(→)**: Sequence node that executes a battery check
- **BatInverter(δ)**: Node that considers success as failure, used to invert status from the battery check
- **Inverter**: node that inverts the result of actions, in this case if the reading from the blackboard fails, ending in a failure the sequence goes on to execute **WanderSeq**
- **SeqTask(→)**: sequence node that execute the main steps to get to the goal 
- **FailIsSucc(δ)**: node that considers failures as success
- **GoalReachedSeq(→)**: sequence node that executes the workflow to get the item and bring it to a desired location
- **WanderSeq(→)**: sequence that executes the wander routine

### Condition Nodes

- **BatteryCheck** - Checks if the battery level is above a threshold
- **GoalReached** - Checks if the previously read item is reached
- **FoundItem** - Checks if the requested item is found

### Action Nodes

- **BatNotify**: Notifies the user if the battery is low
- **GetGoal**: Reads the next item from the blackboard
- **MoveToObj**: Moves the robot to the target item
- **NotifyUser**: Notifies the user if the item is not found
- **Wander**: The robot wanders around the surrounding area
- **AddMark**: The robot adds a marker representing an item on the map

## Behavior Flow

1. The root sequence starts execution
2. Repeats the **SeqGoal**
3. Starts **SeqGoal**
4. Starts **BatSequence**
    - If **BatteryOK** succeeds → **BatInverter** considers it as a failure, this branch is interrupted
    - If **BatteryOK** fails → **BatInverter** considers it as a success
        - Execute **BatNotify**
        - **BatSeqInvert** interrupts the robot actions
5. If the battery is OK, execute **SeqTask**
    -   Reads an Item from the blackboard, if not found the **Inverter** sets the status to success and execute **WanderSeq**
    -   If an item is found moves towards it executing **MoveToObj**
    -   Execute **GoalReachedSeq**:
        - If **GoalReached** succeeds → **Inverter** considers it as a failure, the robot stops
        - If **GoalReached** fails → **FailIsSucc** considers it as a success
            - Execute **NotifyUser**
6. If the item is not found execute **WanderSeq**
    - Execute **Wander**
    - If **FoundItem** fails → the robot stops
    - If **FoundItem** succeeds the item is added to the map through **AddMark**

## Usage
To simulate the tree just execute the main.py script. You can pass the number of desired ticks to be simulated as an argument, so if using uv the command would be `uv run main.py 100` to simulate for 100 ticks. The default is 30