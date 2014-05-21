from behave import *
from threading import Thread
from test_util import *

@given('there is a node')
def step_impl(context):
    create_nodes(context, 1)


@when('we connect')
def step_impl(context):
    context.response = ws_connect(0)


@then('it will introduce itself')
def step_impl(context):
    assert context.response['result']['type'] == u'myself'


@given('there are {num_nodes} connected nodes')
def step_impl(context, num_nodes):
    create_connected_nodes(context, int(num_nodes))


@given('there are {num_nodes} nodes')
def step_impl(context, num_nodes):
    create_nodes(context, int(num_nodes))


@when('node {i} connects to node {j}')
def step_impl(context, i, j):
    ws_send(int(i), 'connect', {'uri': node_addr(int(j))})


@then('node {i} is connected to node {j}')
def step_impl(context, i, j):
    pubkey_j = ws_connect(int(j))[u'result'][u'pubkey']

    response = ws_send(int(i), 'peers')[u'result']
    assert response['type'] == 'peers'
    assert {'pubkey': pubkey_j, 'uri': node_addr(int(j))} in response['peers']


@then('node {i} can query page of node {j}')
def step_impl(context, i, j):
    pubkey_j = ws_connect(int(j))[u'result'][u'pubkey']

    response = ws_send(int(i), 'query_page', {'pubkey': pubkey_j})[u'result']
    data = settings(j)
    print pubkey_j
    print response['text']
    print data['storeDescription']

    assert response[u'type'] == u'page'
    assert response[u'text'] == data['storeDescription']
