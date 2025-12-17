from MultiNode import MultiNode

def init() -> MultiNode:
    return MultiNode('navigator', ['steer'], ['objLocator', 'movePlan'])