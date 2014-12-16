# This file is part of Seastorm
# Copyright 2014 Jakob Kallin

import os.path
import sys
from threading import Thread

import clearinghouse_proxy
import node_manager_proxy
import filesystem_server

def start(key_path, watch_path=None):
	origin_path = os.path.join(os.path.dirname(__file__), 'origin')
	allowed_origin = open(origin_path).read()
	public_key = open(key_path + '.publickey').read()
	private_key = open(key_path + '.privatekey').read()
	
	threads = [
		Thread(target=clearinghouse_proxy.start, kwargs={
			'allowed_origin': allowed_origin
		}),
		Thread(target=node_manager_proxy.start, kwargs={
			'allowed_origin': allowed_origin,
			'public_key': public_key,
			'private_key': private_key
		}),
		Thread(target=filesystem_server.start, kwargs={
			'allowed_origin': allowed_origin,
			'watch_path': watch_path
		})
	]

	for t in threads:
		t.start()
	
	for t in threads:
		t.join()

if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) == 2:
		start(
			key_path=args[0],
			watch_path=args[1]
		)
	elif len(args) == 1:
		start(
			key_path=args[0],
			watch_path=None
		)
	else:
		print 'Usage: seastorm.py key_path file_directory'