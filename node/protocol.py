def hello_request(data):
    data['type'] = 'hello_request'
    return data


def hello_response(data):
    data['type'] = 'hello_reply'
    return data


def goodbye(data):
    data['type'] = 'goodbye'
    return data


def ok():
    return {'type': 'ok'}


def shout(data):
    data['type'] = 'shout'
    return data

def proto_welcome():
    return {'type':'welcome'}

def proto_reputation(pubkey, reviews):
    data = {}
    data['type'] = 'reputation'
    data['pubkey'] = pubkey.encode('hex')
    data['reviews'] = reviews
    return data


def proto_query_reputation(pubkey):
    data = {}
    data['type'] = 'query_reputation'
    data['pubkey'] = pubkey.encode('hex')
    return data


def proto_page(pubkey, text, signature, nickname):
    data = {}
    data['type'] = 'page'
    data['pubkey'] = pubkey
    data['signature'] = signature.encode('hex')
    data['text'] = text
    data['nickname'] = nickname
    return data


def query_page(pubkey):
    data = {}
    data['type'] = 'query_page'
    data['pubkey'] = pubkey.encode('hex')
    return data


def order(id, buyer, seller, state, text, escrows=[], tx=None):
    data = {}
    data['type'] = 'order'
    data['id'] = id
    # this is who signs
    data['buyer'] = buyer.encode('hex')
    # this is who the review is about
    data['seller'] = seller.encode('hex')
    # the signature
    data['escrows'] = escrows
    # the signature
    if data.get('tex'):
        data['tx'] = tx.encode('hex')
    # some text
    data['text'] = text
    # some text
    data['address'] = ''
    data['state'] = state
    # new -> accepted/rejected -> payed -> sent -> received
    return data


def negotiate_pubkey(nickname, ident_pubkey):
    data = {}
    data['type'] = 'negotiate_pubkey'
    data['nickname'] = nickname
    data['ident_pubkey'] = ident_pubkey.encode("hex")
    return data


def proto_response_pubkey(nickname, pubkey, signature):
    data = {}
    data['type'] = "proto_response_pubkey"
    data['nickname'] = nickname
    data['pubkey'] = pubkey.encode("hex")
    data['signature'] = signature.encode("hex")
    return data
