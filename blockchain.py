import datetime
import hashlib
import json
from flask import Flask,jsonify,request
from urllib.parse import urlparse
import requests
from uuid import uuid4
class BlockChain:
	
	def __init__(self):
		self.chain = []
		self.transactions = []
		self.create_block(proof=1, previous_hash = '0')
		self.nodes = set()
	
	def create_block(self,proof,previous_hash):
		block = {
			"index":len(self.chain),
			"timestamp":str(datetime.datetime.now()),
			'proof':proof,
			'transactions':self.transactions,
			'previous_hash':previous_hash
		}

		self.transactions= []
		self.chain.append(block)
		return block

	def add_node(self,address):
		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)

	def replace_chain(self):
		network = self.nodes
		longest_chain = None

		max_length = len(self.chain)

		for node in network:
			response = requests.get('http://' + node + '/get-chain')
			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']
				if length > max_length and self.is_chain_valid(chain):
					max_length = length
					longest_chain = chain

		if longest_chain:
			self.chain = longest_chain
			return True
		
		return False


	def get_previous_block(self):
		return self.chain[-1]
	
	def get_proof_of_work(self, previous_proof):
		new_proof = 1
		flag = False
		while flag is False:
			hash = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
			if hash[:4] == '0000':
				print("Hash is", hash)
				flag = True
			else:
				new_proof = new_proof + 1
		
		return new_proof
	
	def hash(self,block):
		encoded_block = json.dumps(block,sort_keys=True).encode()
		return hashlib.sha256(encoded_block).hexdigest()
	
	def is_chain_valid(self, chain):
		previous_block = chain[0]
		block_index = 1

		while block_index < len(chain):
			block = chain[block_index]
			if block['previous_hash'] != self.hash(previous_block):
				return False
			previous_proof = previous_block['proof']
			proof = block['proof']
			hash = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
			if hash[:4] == '0000':
				print("Hash is", hash)
				return False
			previous_block = block
			block_index = block_index + 1
		
		return True
	
	def add_transaction(self,sender,reciever,amount):
		self.transactions.append({
			'sender':sender,
			'reciever':reciever,
			'amount':amount
		})

		return len(self.transactions)

app = Flask(__name__)

node_address = str(uuid4()).replace('-','')

blockchain = BlockChain()

@app.route('/mine-block',methods=["GET"])
def mine_block_handler():
	"""
	Mines a new block and gives you Sarat coin
	"""
	previous_block = blockchain.get_previous_block()
	previous_proof = previous_block['proof']
	proof = blockchain.get_proof_of_work(previous_proof)
	previous_hash = blockchain.hash(previous_block)
	blockchain.add_transaction(sender=node_address,reciever='Sarat',amount=1)
	block = blockchain.create_block(proof,previous_hash)

	response = {
		"message":"Congrats! You've successfully mined Sarat Coin"
	}

	return jsonify(response)

@app.route('/get-chain',methods = ["GET"])
def get_block_chain():
	response = {'chain': blockchain.chain,"length": len(blockchain.chain)}
	return jsonify(response)

app.run(host="0.0.0.0",port=8080)