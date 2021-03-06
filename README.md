# Parsey Universal Server

A simple Python Flask app to provide Parsey McParseface and its [Cousins](https://github.com/tensorflow/models/blob/master/research/syntaxnet/g3doc/universal.md) over HTTP as an API.

#### The main purpose of this repo is to use POS tagger of Syntaxnet.
#### For retrieving a parsing tree, please modify parser.py function parse_sentence(), uncomment the last return.

### To run:

Run on port 7777:

    $ docker run -it --rm -p 7777:80 jesdoit/parsey-server
    $ docker run -it --rm -p 7777:80 -e PARSEY_MODELS=Swedish,English jesdoit/parsey-server

or detached:

    $ docker run -d -it -p 7777:80 --name parseyserver jesdoit/parsey-server   

The default model is English. To select models set the `PARSEY_MODELS` environment variable. Select one or more (comma separated) models of the ones available [here](https://github.com/tensorflow/models/blob/master/research/syntaxnet/g3doc/universal.md) (NOTE: must be written exactly as it appears in that list)

    $ docker run -it --rm -p 7777:80 -e PARSEY_MODELS=English,Chinese,Swedish JesDoIt/parsey-server

You can also set the batch size if necessary using the `PARSEY_BATCH_SIZE` environment variable (default 1)

### To build:

    $ git clone https://github.com/jesdoit/parsey-universal-server.git
    $ cd parsey-universal-server
    $ docker build -t parseyserver .
    $ docker run -it --rm -p 7777:80 parseyserver

### Demo:

Navigate to http://localhost:7777/demo to view a simple demo.

### To use:

Post plain text, line separated sentences to it:

    $ curl -H "Content-Type:text/plain" -d "Mr. O'Neill thinks that the boys' stories about Chile's capital aren't amusing" http://localhost:7777/

If calling API with Python requests:
    
    import requests
    header = {'Content-Type': 'text/plain'}
    data = "Mr. O'Neill thinks that the boys' stories about Chile's capital aren't amusing"
    r = requests.post("http://localhost:7777/", data=data, headers=headers)
    r.json()


Returns a list of lists of sentences and words, in what is essentially the [CoNLL-U](http://universaldependencies.org/format.html) format, just in JSON:

    [
    [
    {
      "index": 1, 
      "token": "Mr.", 
      "label": "NOUN", 
      "pos": "NN|AN", 
      "parent": 2, 
      "relation": "nmod"
    }, 
    {
      "index": 2, 
      "token": "O'Neill", 
      "label": "PROPN", 
      "pos": "PM|NOM", 
      "parent": 3, 
      "relation": "nsubjpass"
    }, 
    {
      "index": 3, 
      "token": "thinks", 
      "label": "VERB", 
      "pos": "VB|PRS|SFO", 
      "parent": 0, 
      "relation": "ROOT"
    }, 
    {
      "index": 4, 
      "token": "that", 
      "label": "ADJ", 
      "pos": "PC|PRF|NEU|SIN|IND|NOM", 
      "parent": 3, 
      "relation": "xcomp"
    }, 
    {
      "index": 5, 
      "token": "the", 
      "label": "NOUN", 
      "pos": "NN|NEU|SIN|IND|NOM", 
      "parent": 6, 
      "relation": "nmod"
    }, 
    {
      "index": 6, 
      "token": "boys'", 
      "label": "NOUN", 
      "pos": "NN|AN", 
      "parent": 7, 
      "relation": "nsubjpass"
    }, 
    {
      "index": 7, 
      "token": "stories", 
      "label": "VERB", 
      "pos": "VB|PRS|SFO", 
      "parent": 4, 
      "relation": "acl:relcl"
    }, 
    {
      "index": 8, 
      "token": "about", 
      "label": "NOUN", 
      "pos": "NN|UTR|SIN|IND|NOM", 
      "parent": 9, 
      "relation": "nmod"
    }, 
    {
      "index": 9, 
      "token": "Chile's", 
      "label": "PROPN", 
      "pos": "PM|NOM", 
      "parent": 7, 
      "relation": "dobj"
    }, 
    {
      "index": 10, 
      "token": "capital", 
      "label": "NOUN", 
      "pos": "NN|NEU|SIN|IND|NOM", 
      "parent": 7, 
      "relation": "nmod"
    }, 
    {
      "index": 11, 
      "token": "aren't", 
      "label": "ADV", 
      "pos": "AB|AN", 
      "parent": 10, 
      "relation": "cc"
    }, 
    {
      "index": 12, 
      "token": "amusing", 
      "label": "NOUN", 
      "pos": "NN|UTR|SIN|IND|NOM", 
      "parent": 10, 
      "relation": "conj"
    }
    ]
    ]

The default model is the first one in the `PARSEY_MODELS` list (in this case Swedish). To use another, use the `language` query param: (must also match the model name exactly)

    $ curl -H "Content-Type:text/plain" --data-binary "Jag heter JesDoIt" http://localhost:7777/?language=Swedish

Returns:

    [
    [
    {
      "index": 1, 
      "token": "Jag", 
      "label": "PRON", 
      "pos": "PN|UTR|SIN|DEF|SUB", 
      "parent": 2, 
      "relation": "nsubj"
    }, 
    {
      "index": 2, 
      "token": "heter", 
      "label": "VERB", 
      "pos": "VB|PRS|AKT", 
      "parent": 0, 
      "relation": "ROOT"
    }, 
    {
      "index": 3, 
      "token": "JesDoIt", 
      "label": "PROPN", 
      "pos": "PM|NOM", 
      "parent": 2, 
      "relation": "dobj"
    }
    ]
    ]

## Tips
To call the API out of localhost, don't forget enabling the port to remote.
If you are using Google Cloud, here is an example of how to do it in Cloud Shell:
    
    $ gcloud compute firewall-rules create parseyserver --allow tcp:7777
Take a note of your _external ip address_. Now you can access the API out of instance!

#### This [link](https://github.com/tensorflow/models/blob/master/research/syntaxnet/g3doc/CLOUD.md) could help as an instruction of creating Google Cloud instance.




