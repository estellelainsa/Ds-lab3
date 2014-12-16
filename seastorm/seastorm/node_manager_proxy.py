# This file is part of Seastorm
# Copyright 2014 Jakob Kallin

import BaseHTTPServer
import json
import SocketServer
import sys
import urlparse

from node_manager import *

class NodeManagerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	allowed_origin = None
	node_manager = NodeManager()
	public_key = None
	private_key = None
	
	# Because the web application sends POST requests with the content type
	# "application/json" (not "application/x-www-form-urlencoded"), the request
	# must be preflighted using an OPTIONS request.
	def do_OPTIONS(self):
		self.send_response(200)
		self.send_cors_headers()
		self.end_headers()
	
	def do_HEAD(self):
		self.send_response(200)
		self.send_cors_headers()
		self.end_headers()
	
	def do_POST(self):
		try:
			status = 200
			body = self.handle_request()
		except Exception as error:
			status = 500
			body = str(error)
		finally:
			self.send_response(status)
			self.send_cors_headers()
			self.end_headers()
			self.wfile.write(body)
	
	def send_cors_headers(self):
		self.send_header('Content-Type', 'text/plain')
		self.send_header('Access-Control-Allow-Origin', self.allowed_origin)
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')
	
	def handle_request(self):
		url = urlparse.urlparse(self.path)

		# http://example.com/{node_manager_ip}/{node_manager_port}/{function_name}
		# Disregard leading slash.
		node_manager_ip, node_manager_port_str, function_name = url.path.split('/')[1:]
		node_manager_port = int(node_manager_port_str)
		
		public_key, private_key = self.get_keys()
		body = self.get_body()
		params = json.loads(body)
		
		return self.node_manager.call(
			node_manager_ip,
			node_manager_port,
			public_key,
			private_key,
			function_name,
			params
		)
		
	def get_body(self):
		content_length = int(self.headers.getheader('Content-Length'))
		request_body = self.rfile.read(content_length)
		return request_body
	
	def get_keys(self):
		return (self.public_key, self.private_key)

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass
	
def start(allowed_origin, public_key, private_key):
	host = 'localhost'
	port = 5345
	
	NodeManagerHandler.allowed_origin = allowed_origin
	NodeManagerHandler.public_key = public_key
	NodeManagerHandler.private_key = private_key
	
	server = ThreadedHTTPServer((host, port), NodeManagerHandler)
	
	try:
		print 'Starting node manager proxy'
		server.serve_forever()
	except KeyboardInterrupt:
		print 'Stopping node manager proxy'	
		server.server_close()