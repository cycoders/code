from raft_consensus_simulator.models import Node, NodeState

def test_node_defaults():
    n = Node(id=0)
    assert n.state == NodeState.FOLLOWER
    assert n.current_term == 0