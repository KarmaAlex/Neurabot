from MultiNode import MultiNode

def init() -> MultiNode:
    return MultiNode('planner', ['movePlan', 'graspPlan'], ['objLocator', 'reachedObj'])