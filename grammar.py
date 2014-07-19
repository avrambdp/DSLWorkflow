from arpeggio import ZeroOrMore, Kwd, Optional, RegExMatch as _, ParserPython, \
    SemanticAction, OneOrMore, EndOfFile
from arpeggio.export import PMDOTExporter
from export_wf import PWDOTExporter
import pydot

def workflow():         return OneOrMore(task), EndOfFile
def task():             return Kwd('task'), name, open_bracket, ZeroOrMore(nextTask), ZeroOrMore(grType), ZeroOrMore(endTime), ZeroOrMore(exitCondition), close_bracket
def nextTask():         return Kwd('next'), colon, OneOrMore(name, Optional(comma)), semicomma
def grType():           return Kwd('type'), colon, [Kwd('automatic'), Kwd('manual')], semicomma
def endTime():          return Kwd('endTime'), colon, number, "H", semicomma
def exitCondition():    return Kwd('exitCondition'), colon, [name, "None"], semicomma

def name():             return _(r"\w+")
def number():           return _(r"\d+")
    
def open_bracket():     return '('
def close_bracket():    return ')'
def colon():            return ':'
def comma():            return ','
def semicomma():        return ';'   
    
class DSLflow():
    
    def __init__(self):
        self.parser = ParserPython(workflow, debug=True)
        
    def create(self, input_workflow):                        
        try:            
            parse_tree = self.parser.parse(input_workflow)                
            PWDOTExporter().exportFile(parse_tree, "workflow.dot")        
            graph = pydot.graph_from_dot_file('workflow.dot')            
            graph.write_png('workflow.png')
            
        except Exception:
            print "Language error..."
