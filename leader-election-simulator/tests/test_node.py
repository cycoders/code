import random

from leader_election_simulator.node import Node


def test_init_node(node):
    assert node.state == "follower"
    assert node.current_term == 0
    assert node.voted_for is None
    assert len(node.votes_received) == 0
    assert 250 <= node.election_timeout <= 500
    assert node.is_active


def test_become_candidate(node):
    old_term = node.current_term
    node.become_candidate()
    assert node.state == "candidate"
    assert node.current_term == old_term + 1
    assert node.voted_for == "test"
    assert node.votes_received == {"test"}
    assert node.election_timeout_counter == 0
    assert 250 <= node.election_timeout <= 500


def test_become_leader(node):
    node.become_candidate()  # setup votes
    node.votes_received.add("other1")
    node.votes_received.add("other2")  # majority for 5
    node.become_leader()
    assert node.state == "leader"
    assert node.election_timeout_counter == 0
    assert len(node.votes_received) == 0  # cleared


def test_handle_higher_term(node):
    other = Node("other", 5)
    other.current_term = 2
    node.handle_msg("request_vote", other, 2)
    assert node.current_term == 2
    assert node.state == "follower"
    assert node.voted_for is None
    assert len(node.votes_received) == 0


def test_handle_vote_grant(node):
    other = Node("other", 5)
    other.become_candidate()
    node.handle_msg("request_vote", other, 1)
    assert node.voted_for == "other"
    assert len(other.votes_received) == 2  # self + node


def test_timeout_triggers_election(node):
    node.election_timeout_counter = node.election_timeout + 1
    node.tick()
    assert node.state == "candidate"