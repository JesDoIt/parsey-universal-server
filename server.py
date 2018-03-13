#!/usr/bin/python3

# sudo apt-get install python3-pip
# sudo pip3 install flask

import os
from flask import Flask, request, Response
from multiprocessing import Pool
from parser import parse_sentence, MODELS
import json

app = Flask(__name__)
port = 80 if os.getuid() == 0 else 8000

pool = Pool(1, maxtasksperchild=50)

@app.route('/', methods = ['POST', 'GET'])
def index():

  data = request.args.get("q", "")
  if not data:
      data = request.data.decode('utf-8')
  if not data:
      return Response(status=500, response="error")
      
  print("got something: '%s'" % data)
  result = pool.apply(parse_sentence, [data, request.args])

  return Response(
    response=json.dumps(result, indent=2),
    status=200,
    content_type="application/json")

@app.route('/demo')
def demo():
    print("Serving demo? %s" % app.root_path)
    return app.send_static_file('demo.html')
  
@app.route('/available-models')
def available_models():
    print("Available models? %s" % MODELS)
    return Response(status=200,response=json.dumps(MODELS),content_type="application/json")

 if __name__ == '__main__':
    app.run(port=port, host="0.0.0.0")
