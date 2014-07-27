from arpeggio import ZeroOrMore, Kwd, Optional, RegExMatch as _, ParserPython, \
    SemanticAction, OneOrMore, EndOfFile
from arpeggio.export import PMDOTExporter, PTDOTExporter
from export_wf import PWDOTExporter
import pydot
from models import *

def workflow():         return Kwd('workflow'), name, open_bracket, OneOrMore(task), close_bracket, EndOfFile
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
            
    def run(self):
        """Running semantic analysis and storing workflow object in database"""
        
        #connect to database
        mysql_db.connect()
    
        #create tables if not exists
        WorkflowOM.create_table(True)
        TaskOM.create_table(True)    
        NextTaskOM.create_table(True) 
        
        #run semantic analyzer
        workflow_obj = self.parser.getASG()
        
        #save workflow object and tasks in database
        workflow_obj.save()
        
        for task in workflow_obj.tasks_list:
            task.workflow = workflow_obj        #after saving in database workflow_obj get id
            task.save()
            
        #save next tasks    
        for task in workflow_obj.tasks_list:
            for next in task.next_tasks:
                nextTask = NextTaskOM(from_task = task, to_task = next)
                nextTask.save()
        
        #close database connection
        mysql_db.close()
        
        
        
class WorkflowSA(SemanticAction):            
    def first_pass(self, parser, node, children):        
        workflow = WorkflowOM(tasks_list = [])
        
        for child in children:
            if isinstance(child, TaskOM):
                child.workflow = workflow
                workflow.tasks_list.append(child)
            if isinstance(child, NameOM):   
                workflow.name = child.value      
                
        return workflow
        
class TaskSA(SemanticAction):    
    def first_pass(self, parser, node, children):
        task = TaskOM(next_tasks = [])
        
        for child in children:
            if isinstance(child, NameOM):
                task.name = child.value
            if isinstance(child, NextTaskOM):
                task.next_tasks = child.names
                
        return task
    
    def second_pass(self,sa_name, task):        
        """Replacing next task name with next task object"""
        
        print task.next_tasks
        
        next_tasks_obj = []
        
        for next_task_name in task.next_tasks:
            for next_task_obj in task.workflow.tasks_list:
                if next_task_name == next_task_obj.name:
                    next_tasks_obj.append(next_task_obj)
                    
        task.next_tasks = next_tasks_obj
                            
        return task

class NextTaskSA(SemanticAction):
    def first_pass(self, parser, node, children):
        nextTask = NextTaskOM(names = [])
        
        for child in children:
            if isinstance(child, NameOM):
                nextTask.names.append(child.value)
                
        return nextTask

class NameSA(SemanticAction):    
   def first_pass(self, parser, node, children):       
        return NameOM(str(node))
        
workflow.sem = WorkflowSA()
task.sem = TaskSA() 
nextTask.sem = NextTaskSA()
name.sem = NameSA()
    
