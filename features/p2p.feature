Feature: Websocket Client Interface

  Scenario: Connection
    Given there is a node
     When we connect
     Then it will introduce itself 

  Scenario: Connect to a node
    Given there are 2 nodes
    When node 0 connects to node 1 
    Then node 0 is connected to node 1
    And node 1 is connected to node 0

  Scenario: Peer discovery
    Given there are 3 nodes
    When node 0 connects to node 1 
    And node 1 connects to node 2
    Then node 0 is connected to node 1
    And node 1 is connected to node 0
    And node 1 is connected to node 2
    And node 2 is connected to node 1
    And node 0 is connected to node 2
    And node 2 is connected to node 0

  Scenario: Fetch Market Page
    Given there are 2 connected nodes
    Then node 0 can query page of node 1

  # Fails
  # Scenario: Fetch Market Page
  #   Given there are 3 connected nodes
  #   Then node 0 can query page of node 1
  #   And node 0 can query page of node 2
