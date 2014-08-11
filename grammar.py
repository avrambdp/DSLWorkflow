from arpeggio import ZeroOrMore, Kwd, Optional, RegExMatch as _, ParserPython, \
    SemanticAction, OneOrMore, EndOfFile
from arpeggio.export import PMDOTExporter, PTDOTExporter
from export_wf import PWDOTExporter
import pydot
import os

def workflow():         return Kwd('workflow'), name, open_bracket, ZeroOrMore(role), Optional(description), OneOrMore(task), close_bracket, EndOfFile
def task():             return Kwd('task'), name, open_bracket, ZeroOrMore(role), ZeroOrMore(nextTask), ZeroOrMore(grType), ZeroOrMore(endTime), ZeroOrMore(exitCondition), Optional(description), close_bracket
def nextTask():         return Kwd('next'), colon, OneOrMore(name, Optional(comma)), semicomma
def grType():           return Kwd('type'), colon, [Kwd('automatic'), Kwd('manual')], semicomma
def endTime():          return Kwd('deadline'), colon, number, "H", semicomma
def exitCondition():    return Kwd('exitCondition'), colon, name, semicomma
def role():             return Kwd('role'), colon, OneOrMore(name, Optional(comma)), semicomma
def description():      return Kwd('description'), colon, quote, text, quote, semicomma
 
def name():             return _(r"\w+")
def number():           return _(r"\d+")
def text():             return _(r"[\w\s]+")
    
def open_bracket():     return '('
def close_bracket():    return ')'
def colon():            return ':'
def comma():            return ','
def semicomma():        return ';'   
def quote():            return '"'  

class DSLflow():
    
    def __init__(self):
        self.parser = ParserPython(workflow, debug=True)
        
    def create(self, input_workflow):                        
#         try:            
        parse_tree = self.parser.parse(input_workflow)                
        PWDOTExporter().exportFile(parse_tree, "workflow.dot")        
        graph = pydot.graph_from_dot_file('workflow.dot')            
        graph.write_png('workflow.png')
            
#         except Exception:
#             print "Language error..."
            
    def upload(self, model):        
        try:
            path = "D:\\Fax\\master_rad\\projekat\\web_tasks_process\\tasks\\models\\"
            file_name = self.parser.getASG()
            ext = ".wf"
            
            full_path = path + str(file_name) + ext
            
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path))
            with open(full_path, "w") as file:
                file.write(model)
                file.close()
            
            return True
        except Exception:
            return False
        
class WorkflowSA(SemanticAction):
    def first_pass(self, parser, node, children):  
        return [child.value for child in children if isinstance(child, NameOM)][0]     
    
class NameSA(SemanticAction):
    def first_pass(self, parser, node, children):
        return NameOM(node)
    
workflow.sem = WorkflowSA()
name.sem = NameSA()
        
class NameOM():
    def __init__(self, value=None):
        self.value = value
   
