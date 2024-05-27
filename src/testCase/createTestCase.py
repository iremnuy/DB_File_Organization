import random
import time

def current_unix_time():
    return int(time.time())

class Type:
    def __init__(self, name, primaryKeyIndex, fields):
        self.name = name
        self.primaryKeyIndex = primaryKeyIndex
        self.fields = fields
        self.records = {}
        self.deletedRecords = {}
    
    def createRecord(self, values):
        primaryKey = values[self.primaryKeyIndex - 1]
        if primaryKey in self.records:
            return False
        self.records[primaryKey] = values
        return True
    
    def deleteRecord(self, primaryKey):
        if primaryKey not in self.records:
            return False
        self.deletedRecords[primaryKey] = self.records[primaryKey]
        del self.records[primaryKey]
        return True
    
    def findRecord(self, primaryKey):
        if primaryKey in self.records:
            return self.records[primaryKey]
        return None


inputLines = []
outputLines = []
logLines = []
types = {}

maxNameLength = 12
maxFieldNameLength = 20
maxFields = 6

def createType():
    name = "".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, maxNameLength))])
    while name in types:
        name = "".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, maxNameLength))])
    
    numFields = random.randint(1, maxFields)
    fields = []
    for _ in range(numFields):
        fieldName = "".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, maxFieldNameLength))])
        fieldType = random.choice(['int', 'str'])
        fields.append(f"{fieldName} {fieldType}")
    
    primaryKeyIndex = random.randint(1, numFields)
    type = Type(name, primaryKeyIndex, fields)
    types[name] = type

    operation = f"create type {name} {numFields} {primaryKeyIndex} {' '.join(fields)}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, success")

def createExistingType():

    name = random.choice(list(types.keys()))

    numFields = random.randint(1, maxFields)
    fields = []
    for _ in range(numFields):
        fieldName = "".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, maxFieldNameLength))])
        fieldType = random.choice(['int', 'str'])
        fields.append(f"{fieldName} {fieldType}")
    
    primaryKeyIndex = random.randint(1, numFields)
    
    operation = f"create type {name} {numFields} {primaryKeyIndex} {' '.join(fields)}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, failure")

def createRecord():
    typeName = random.choice(list(types.keys()))
    type = types[typeName]
    primaryKeyIndex = type.primaryKeyIndex

    values = []
    for field in type.fields:
        if field.split()[1] == 'int':
            values.append(str(random.randint(1, 100)))
        else:
            values.append("".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, 10))]))
    
    while type.findRecord(values[primaryKeyIndex - 1]):
        values = []
        for field in type.fields:
            if field.split()[1] == 'int':
                values.append(str(random.randint(1, 100)))
            else:
                values.append("".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, 10))]))
    
    if values[primaryKeyIndex - 1] in type.deletedRecords:
        type.deletedRecords.pop(values[primaryKeyIndex - 1])    
    type.createRecord(values)
    
    operation = f"create record {typeName} {' '.join(values)}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, {'success'}")

def createExistingRecord():
    typeName = random.choice(list(types.keys()))
    type = types[typeName]
    primaryKeyIndex = type.primaryKeyIndex

    try:
        primaryKey = random.choice(list(type.records.keys()))
    except:
        return
    values = []
    for index,field in enumerate(type.fields):
        if index == primaryKeyIndex - 1:
            values.append(primaryKey)
        else:
            if field.split()[1] == 'int':
                values.append(str(random.randint(1, 100)))
            else:
                values.append("".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, 10))]))

    operation = f"create record {typeName} {' '.join(values)}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, {'failure'}")

def deleteRecord():
    typeName = random.choice(list(types.keys()))
    type = types[typeName]
    try:
        primaryKey = random.choice(list(type.records.keys()))
    except:
        return
    type.deleteRecord(primaryKey)

    operation = f"delete record {typeName} {primaryKey}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, {'success'}")

def deleteNonExistentRecord():
    typeName = random.choice(list(types.keys()))
    type = types[typeName]
    primaryKey = ""
    if type.deletedRecords:
        primaryKey = random.choice(list(type.deletedRecords.keys()))
    else:
        if type.fields[type.primaryKeyIndex - 1].split()[1] == 'int':
            primaryKey = str(random.randint(1, 100))
        else:
            primaryKey = "".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, 10))])
    
    if primaryKey in type.records:
        return
    
    type.deleteRecord(primaryKey)
    
    operation = f"delete record {typeName} {primaryKey}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, {'failure'}")

def searchRecord():
    typeName = random.choice(list(types.keys()))
    type = types[typeName]
    try:
        primaryKey = random.choice(list(type.records.keys()))
    except:
        return

    operation = f"search record {typeName} {primaryKey}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, {'success'}")
    outputLines.append(f"{' '.join(type.records[primaryKey])}")

def searchNonExistentRecord():
    typeName = random.choice(list(types.keys()))
    type = types[typeName]
    primaryKey = ""
    if type.deletedRecords:
        primaryKey = random.choice(list(type.deletedRecords.keys()))
    else:
        if type.fields[type.primaryKeyIndex - 1].split()[1] == 'int':
            primaryKey = str(random.randint(1, 100))
        else:
            primaryKey = "".join([chr(random.randint(97, 122)) for _ in range(random.randint(1, 10))])
    
    if primaryKey in type.records:
        return
    
    operation = f"search record {typeName} {primaryKey}"
    inputLines.append(operation)
    logLines.append(f"{current_unix_time()}, {operation}, {'failure'}")



def createTestCase():
    for _ in range(3):
        createType()

    for _ in range(20):
        createRecord()

    operations = 0
    
    while operations < 2000:
        randint = random.randint(1, 8000)
        if randint <= 40:
            createType()
            operations += 1
        elif 1000 <= randint <= 1150:
            createExistingType()
            operations += 1
        elif 2000 < randint <= 3000:
            createRecord()
            operations += 1
        elif 3000 < randint <= 3300:
            createExistingRecord()
            operations += 1
        elif 4000 < randint <= 4200:
            deleteRecord()
            operations += 1
        elif 5000 < randint <= 5150:
            deleteNonExistentRecord()
            operations += 1
        elif 6000 < randint <= 6400:
            searchRecord()
            operations += 1
        elif 7000 < randint <= 7200:
            searchNonExistentRecord()
            operations += 1
    
    with open("input.txt", 'w') as file:
        file.write('\n'.join(inputLines))
    
    with open("output_test.txt", 'w') as file:
        file.write('\n'.join(outputLines))
    
    with open("log_test.txt", 'w') as file:
        file.write('\n'.join(logLines))

createTestCase()