from peewee import *

mysql_db = MySQLDatabase('test', user='root', password='admin')

class MySQLModel(Model):
    """A base model that will use our MySQL database""" 
    
    class Meta:
        database = mysql_db

class WorkflowOM(MySQLModel):
    """Work flow database model"""
    
    name = CharField()
                        
    class Meta:
        db_table = 'workflow'
        
class TaskOM(MySQLModel):
    """Task database model"""
    
    name = CharField()
    workflow = ForeignKeyField(WorkflowOM, related_name="tasks")
    
    class Meta:
        db_table = 'task'

class NextTaskOM(MySQLModel):
    """Next task database model"""
    
    from_task = ForeignKeyField(TaskOM, related_name='relationships')
    to_task = ForeignKeyField(TaskOM, related_name='related_to')
    
    class Meta:
        db_table = 'next_tasks'

class Group(MySQLModel):
    """Users group database model"""
    
    name = CharField()

class User(MySQLModel):
    """User database model"""
    
    name = CharField()
    group = ForeignKeyField(Group, related_name='users')
    
class NameOM(): 
    """Name model"""
       
    def __init__(self, value = None):
        self.value = value

