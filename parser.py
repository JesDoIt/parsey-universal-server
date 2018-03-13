#!/usr/bin/python3

from collections import OrderedDict
import subprocess, os

ROOT_DIR = "models/syntaxnet"
PARSER_EVAL = "bazel-bin/syntaxnet/parser_eval"
#MODEL_DIR = "syntaxnet/models/parsey_mcparseface"
MODEL_DIR = "syntaxnet/models/parsey_universal/"
MODELS = [l.strip() for l in os.getenv('PARSEY_MODELS', 'English').split(',')]

def open_parser_eval(args):
    return subprocess.Popen(
        [PARSER_EVAL] + args,
        cwd=ROOT_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
        )

def send_input(process, input_str, num_lines):
    input_str = input_str.encode("utf8")
    process.stdin.write(input_str)
    process.stdin.write(b"\n\n") # signal end of documents
    process.stdin.flush()
    response = b""
    while num_lines > 0:
        line = process.stdout.readline()
        if line.strip() == b"":
            # empty line signals end of output for one sentence
            num_lines -= 1
        response += line
    return response.decode("utf8")

def create_pipeline(model):
    #Tokenizer

    #Open the morpher
    morpher = open_parser_eval([
        "--input=stdin",
        "--output=stdout-conll",
        "--hidden_layer_sizes=64",
        "--arg_prefix=brain_morpher",
        "--graph_builder=structured",
        "--task_context=" + MODEL_DIR + "/context.pbtxt",
        "--resource_dir=" + MODEL_DIR + model,
        "--model_path=" + MODEL_DIR  + model + "/morpher-params",
        "--slim_model",
        "--batch_size=1",
        "--alsologtostderr",
    ])
    
    # Open the part-of-speech tagger.
    pos_tagger = open_parser_eval([
        "--input=stdin",
        "--output=stdout-conll",
        "--hidden_layer_sizes=64",
        "--arg_prefix=brain_tagger",
        "--graph_builder=structured",
        "--task_context=" + MODEL_DIR + "/context.pbtxt",
        "--resource_dir=" + MODEL_DIR + model,
        "--model_path=" + MODEL_DIR  + model + "/tagger-params",
        "--slim_model",
        "--batch_size=1",
        "--alsologtostderr",
    ])

    # Open the syntactic dependency parser.
    dependency_parser = open_parser_eval([
        "--input=stdin-conll",
        "--output=stdout-conll",
        "--hidden_layer_sizes=512,512",
        "--arg_prefix=brain_parser",
        "--graph_builder=structured",
        "--task_context=" + MODEL_DIR + "/context.pbtxt",
        "--resource_dir=" + MODEL_DIR + model,
        "--model_path=" + MODEL_DIR  + model + "/parser-params",
        #"--model_path=" + MODEL_DIR + "/parser-params",
        "--slim_model",
        "--batch_size=1024",
        "--alsologtostderr",
    ])
    return [morpher, pos_tagger, dependency_parser]
   # return [tokenizer, pos_tagger, dependency_parser]
def split_tokens(parse):
    # Format the result.
    def format_token(line):
        x = OrderedDict(zip(["index", "token", "lemma", "label", "pos", "unknown2", "parent", "relation", "unknown3", "unknown4"],line.split("\t")))
        x["index"] = int(x["index"])
        x["parent"] = int(x["parent"])
        for key, val in x.items():
            if val == "_":
                del x[key]
        #del x["lemma"]
        #del x["unknown2"]
        #del x["unknown3"]
        #del x["unknown4"]
        return x

    return [
        format_token(line)  
        for line in parse.strip().split("\n")
  ]
def magic(split_tokens, sentence):
    tokens = { tok["index"]: tok for tok in split_tokens }
    tokens[0] = OrderedDict([ ("sentence", sentence) ])
    for tok in split_tokens:
       tokens[tok['parent']]\
         .setdefault('tree', OrderedDict()) \
         .setdefault(tok['relation'], []) \
         .append(tok)
       del tok['parent']
       del tok['relation']
    return tokens[0]

pipelines = {}
for model in MODELS:
    pipelines[model] = create_pipeline(model)

def parse_sentence(sentences,request_args):
    sentences = sentences.strip()
    num_lines = sentences.count("\n") + 1
    lang = request_args.get('language', default=MODELS[0])
    pipeline = pipelines[lang]
    # Do tokenization
    #tokenized = send_input(pipeline[0], sentences + "\n", num_lines)
    #Do morphing.
    #morphed = send_input(pipeline[0], sentences + "\n", num_lines)
    
    # Do POS tagging.
    #pos_tags = send_input(pipeline[1], morphed, num_lines)
    pos_tags = send_input(pipeline[1], sentences+"\n", num_lines)
    # Do syntax parsing.
    #dependency_parse = send_input(dependency_parser, pos_tags, num_lines)
    dependency_parse = send_input(pipeline[2], pos_tags, num_lines)
    # Split and make the trees.
    dependency_parse_list = dependency_parse.strip().split("\n\n")
    split_tokens_list = map(split_tokens, dependency_parse_list)
    # Here be magic
    #return [magic(st, sen) for sen, st in zip(sentences.split("\n"), split_tokens_list)]
    return split_tokens_list
if __name__ == "__main__":
    import sys, pprint
    pprint.pprint(parse_sentence(sys.stdin.read().strip())["tree"])
