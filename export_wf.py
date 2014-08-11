# -*- coding: utf-8 -*-
#######################################################################
# Name: export_wf.py
# Purpose: Export support for arpeggio
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License

# Modified for grammar export - Avram
#######################################################################

import io
from arpeggio import Terminal


class Exporter(object):
    """
    Base class for all Exporters.
    """

    def __init__(self):
        super(Exporter, self).__init__()

        # Export initialization
        self._render_set = set()  # Used in rendering to prevent
                                        # rendering
                                        # of the same node multiple times

        self._adapter_map = {}  # Used as a registry of adapters to
                                        # ensure that the same adapter is
                                        # returned for the same adaptee object

    def export(self, obj):
        """
        Export of an obj to a string.
        """
        self._outf = io.StringIO()
        self._export(obj)
        return self._outf.getvalue()

    def exportFile(self, obj, file_name):
        """
        Export of obj to a file.
        """
        self._outf = open(file_name, "w")
        self._export(obj)
        self._outf.close()

    def _export(self, obj):
        self._outf.write(self._start())
        self._render_node(obj)
        self._outf.write(self._end())

    def _start(self):
        """
        Override this to specify the beginning of the graph representation.
        """
        return ""

    def _end(self):
        """
        Override this to specify the end of the graph representation.
        """
        return ""


class ExportAdapter(object):
    """
    Base adapter class for the export support.
    Adapter should be defined for every export and graph type.

    Attributes:
        adaptee: A node to adapt.
        export: An export object used as a context of the export.
    """
    def __init__(self, node, export):
        self.adaptee = node  # adaptee is adapted graph node
        self.export = export


# -------------------------------------------------------------------------
# Support for DOT language


class DOTExportAdapter(ExportAdapter):
    """
    Base adapter class for the DOT export support.
    """
    @property
    def id(self):
        """
        Graph node unique identification.
        """
        raise NotImplementedError()

    @property
    def desc(self):
        """
        Graph node textual description.
        """
        raise NotImplementedError()

    @property
    def neighbours(self):
        """
        A set of adjacent graph nodes.
        """
        raise NotImplementedError()


class PMDOTExportAdapter(DOTExportAdapter):
    """
    Adapter for ParsingExpression graph types (parser model).
    """
    @property
    def id(self):
        return id(self.adaptee)

    @property
    def desc(self):
        return self.adaptee.desc

    @property
    def neighbours(self):
        if not hasattr(self, "_neighbours"):
            self._neighbours = []

            # Registry of adapters used in this export
            adapter_map = self.export._adapter_map

            for c, n in enumerate(self.adaptee.nodes):
                if isinstance(n, PMDOTExportAdapter):
                    # if the neighbour node is already adapted use that adapter
                    self._neighbours.append((str(c + 1), n))
                elif id(n) in adapter_map:
                    # current node is adaptee -> there is registered adapter
                    self._neighbours.append((str(c + 1), adapter_map[id(n)]))
                else:
                    # Create new adapter
                    adapter = PMDOTExportAdapter(n, self.export)
                    self._neighbours.append((str(c + 1), adapter))
                    adapter_map[adapter.id] = adapter

        return self._neighbours


class PTDOTExportAdapter(PMDOTExportAdapter):
    """
    Adapter for ParseTreeNode graph types.
    """
    @property
    def neighbours(self):
        if isinstance(self.adaptee, Terminal):
            return []
        else:
            if not hasattr(self, "_neighbours"):
                self._neighbours = []
                for c, n in enumerate(self.adaptee):
                    adapter = PTDOTExportAdapter(n, self.export)
                    self._neighbours.append((str(c + 1), adapter))
            return self._neighbours


class DOTExporter(Exporter):
    """
    Export to DOT language (part of GraphViz, see http://www.graphviz.org/)
    """
    def _render_node(self, node):
        if not node in self._render_set:
            self._render_set.add(node)
            self._outf.write('\n%s [label="%s"];' % 
                             (node.id, self._dot_label_esc(node.desc)))
            # TODO Comment handling
#            if hasattr(node, "comments") and root.comments:
#                retval += self.node(root.comments)
#                retval += '\n%s->%s [label="comment"]' % \
                            # (id(root), id(root.comments))
            for name, n in node.neighbours:
                self._outf.write('\n%s->%s [label="%s"]' % 
                                 (node.id, n.id, name))
                self._outf.write('\n')
                self._render_node(n)

    def _start(self):
        return "digraph arpeggio_graph {"

    def _end(self):
        return "\n}"

    def _dot_label_esc(self, to_esc):
        to_esc = to_esc.replace("\\", "\\\\")
        to_esc = to_esc.replace('\"', '\\"')
        to_esc = to_esc.replace('\n', '\\n')
        return to_esc


class PMDOTExporter(DOTExporter):
    """
    A convenience DOTExport extension that uses ParserExpressionDOTExportAdapter
    """
    def export(self, obj):
        return super(PMDOTExporter, self).\
            export(PMDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PMDOTExporter, self).\
            exportFile(PMDOTExportAdapter(obj, self), file_name)


class PTDOTExporter(DOTExporter):
    """
    A convenience DOTExport extension that uses PTDOTExportAdapter
    """
    def export(self, obj):
        return super(PTDOTExporter, self).\
            export(PTDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PTDOTExporter, self).\
            exportFile(PTDOTExportAdapter(obj, self), file_name)
            
class PWDOTExporter(DOTExporter):        
        
    def _render_node(self, node): 
        self.tasks_id = []  # Used as list for storing tasks id's
        self.tasks_id_name = {}  # Used as dictionary for storing key value pairs (task id, task name)
        self.tasks_rel = {}  # Used as dictionary for storing relations between tasks, as key value pairs (to task id, from task id)
        self.tasks_end = []  # Used for storing tasks that ends process
        
        self.next_task_rendering = False  # If true parent task name rendering, if false task name rendering        
        self.task_rendering = False
        self.role_rendering = False
        
        self._rendering_node(node)   
                        
        self._creating_diagram()
                
    def _rendering_node(self, node):      
        
        if not node in self._render_set: 
            
            self._render_set.add(node)
                        
            if(node.desc.startswith('task')):             
                self.tasks_id.append(str(node.id))                                
                self.next_task_rendering = False
                self.task_rendering = True
                self.role_rendering = False
            
            if(node.desc.startswith('name')):                
                if self.task_rendering and not (self.role_rendering):     
                        
                    first_index = (node.desc).index('\'') + 1
                    last_index = (node.desc).rindex('\'')
                    
                    task_name = node.desc[first_index:last_index]
                    task_id = str(self.tasks_id[-1])
                    
                    if(self.next_task_rendering): 
                        self.tasks_rel.setdefault(task_id, []).append(task_name)      
                    else:
                        self.tasks_id_name[task_id] = task_name
          
            if(node.desc.startswith('next')):                 
                self.next_task_rendering = True  
                self.role_rendering = False
                
            if(node.desc.startswith('exitCondition') or node.desc.startswith('workflow')):     
                self.task_rendering = False              
            
            if(node.desc.startswith('role')):
               self.role_rendering = True
            
            for _, n in node.neighbours:
                self._rendering_node(n)
                
    def _creating_diagram(self):                
                 
            print "ID NAMES:"
            print self.tasks_id_name
                
            print "TASK RELATIONS:"
            print self.tasks_rel
            
            # Replacing names with id's
            for key, name in self.tasks_id_name.items():
                for from_id, to_ids in self.tasks_rel.items():        
                    self.tasks_rel[from_id] = [key if x == name else x for x in to_ids]
                                
            # Writing nodes/tasks
            for key in self.tasks_id:
                self._outf.write('\n%s [label="%s"];\n' % 
                             (key, self.tasks_id_name[str(key)]))
            
            tasks_end = list(self.tasks_id)
            tasks_start = list(self.tasks_id)
            
            # Writing relations between nodes/tasks
            for from_task, to_tasks in self.tasks_rel.items():                               
                if from_task in str(tasks_end):
                    tasks_end.remove(from_task)
                            
                gateway = False
                
                if len(to_tasks) > 1:                
                    self._outf.write('\nnext%s [shape=diamond]\n' % from_task)
                    self._outf.write('\n%s->next%s\n' % 
                                     (from_task, from_task))
                    gateway = True
                                
                #print "1:" + str(to_tasks)
                for to_task in to_tasks: 
                    if gateway:                        
                        self._outf.write('\nnext%s->%s\n' % 
                                     (from_task, to_task))
                    else:               
                        self._outf.write('\n%s->%s\n' % 
                                     (from_task, to_task))
                        
                    #print "2:" + str(tasks_start)
                    #print "3:" + str(to_task)
                    
                    if to_task in str(tasks_start):
                        tasks_start.remove(to_task)                 
                        
            # set start process
            if(len(tasks_start)) > 1:
                self._outf.write('\nnextStartProcess [shape=diamond]\n')
                self._outf.write('\nstartProcess->nextStartProcess\n')
                for i in range(len(tasks_start)):  
                    self._outf.write('\nnextStartProcess->%s\n' % str(tasks_start[i]))
            else:
                self._outf.write('\nstartProcess->%s\n' % str(tasks_start[0]))                        
                       
            # set end process         
            for i in range(len(tasks_end)):
                self._outf.write('\nendProcess%s [shape=circle, penwidth=3]\n' % str(i))
                self._outf.write('\n%s->endProcess%s\n' % (str(tasks_end[i]), str(i)))                
            
    def _start(self):
        return "digraph arpeggio_graph { \
                    \nnode [shape=box, color=Red, fontname=Courier, label=\"\"] \
                    \nedge [color=Blue] \
                    \nstartProcess [shape=circle] \
                    \nrankdir=\"LR\"\n"
            
    def export(self, obj):
        return super(PTDOTExporter, self).\
            export(PTDOTExportAdapter(obj, self))

    def exportFile(self, obj, file_name):
        return super(PWDOTExporter, self).\
            exportFile(PTDOTExportAdapter(obj, self), file_name)

