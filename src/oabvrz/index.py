import os
import pickle
import sys

class BPlusTreeNode:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.keys = [] #for internal nodes this will direct the search to the correct child, for leaf nodes, it will be the key value
        self.children = []

class BPlusTree:
    def __init__(self, max_keys=4):  #each node has at most 4 keys, if a node has more than 4 keys, new node will be created
        self.root = BPlusTreeNode()
        self.max_keys = max_keys

    def search(self, key):
        print("searching key: ", key)
        current_node = self.root
        #if the searched key is from a different type do not search and retrun none 
        #if current node is null return none directly 
        try:
            while not current_node.is_leaf:
                i = 0
                while i < len(current_node.keys) and key >= current_node.keys[i]:
                    i += 1
                current_node = current_node.children[i]

            for i, item in enumerate(current_node.keys):
                print("item is ", item)
                print("key is ", key)
                if item == key:
                    return current_node.children[i]
            return None
        except Exception as e:
            print("Error for key : ", e)
            return None #key type error, or empty tree

    def insert(self, key, record_pointer):
        print("inserting key: ", key)
        root = self.root
        if len(root.keys) == self.max_keys:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0, self.root)
            self.root = new_root

        self.insert_non_full(self.root, key, record_pointer)

    def insert_non_full(self, node, key, record_pointer):
        if node.is_leaf:
            i = len(node.keys) - 1
            node.keys.append(None)
            node.children.append(None)
            while i >= 0 and key < node.keys[i]:
                print("node.keys[i] is ", node.keys[i])
                print("node.keys[i+1] is ", node.keys[i+1])
                print("node.children list is ", node.children)
                node.keys[i+1] = node.keys[i] 
                node.children[i+1] = node.children[i] 
                i -= 1
            node.keys[i+1] = key
            print("i is ", i)
            node.children[i+1] = record_pointer #gives index out of range error for 4,4
        else:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == self.max_keys:
                self.split_child(node, i, node.children[i])
                if key > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], key, record_pointer)

    def split_child(self, parent, index, child):
        new_node = BPlusTreeNode(is_leaf=child.is_leaf)
        mid = self.max_keys // 2

        # Add mid key to parent
        parent.keys.insert(index, child.keys[mid])
        parent.children.insert(index + 1, new_node)

        # Distribute keys and children
        new_node.keys = child.keys[mid + 1:]
        new_node.children = child.children[mid + 1:] if not child.is_leaf else child.children[mid:]

        child.keys = child.keys[:mid]
        child.children = child.children[:mid + 1] if not child.is_leaf else child.children[:mid]


    def delete(self, key):
        self.delete_from_node(self.root, key)
        # If the root is empty and has children, make the first child the new root
        if not self.root.keys and self.root.children:
            self.root = self.root.children[0]

    def delete_from_node(self, node, key):
        if node.is_leaf:
            if key in node.keys:
                index = node.keys.index(key)
                node.keys.pop(index)
                node.children.pop(index)
                return True
            return False
        else:
            index = self.find_key_index(node, key)
            if index < len(node.keys) and node.keys[index] == key:
                # Key is in the internal node
                return self.delete_from_internal_node(node, index)
            else:
                # Key is in a child node
                if self.delete_from_node(node.children[index], key):
                    # Handle underflow
                    if len(node.children[index].keys) < self.max_keys // 2:
                        self.handle_underflow(node, index)
                    return True
                return False

    def find_key_index(self, node, key):
        for i, item in enumerate(node.keys):
            if key < item:
                return i
        return len(node.keys)

    def delete_from_internal_node(self, node, index):
        key = node.keys[index]
        # Replace key with the largest key from the left subtree
        predecessor = self.get_predecessor(node, index)
        node.keys[index] = predecessor
        self.delete_from_node(node.children[index], predecessor)
        # Handle underflow
        if len(node.children[index].keys) < self.max_keys // 2:
            self.handle_underflow(node, index)
        return True

    def get_predecessor(self, node, index):
        current = node.children[index]
        while not current.is_leaf:
            current = current.children[-1]
        return current.keys[-1]

    def handle_underflow(self, node, index):
        if index > 0 and len(node.children[index - 1].keys) > self.max_keys // 2:
            # Borrow from left sibling
            self.borrow_from_left(node, index)
        elif index < len(node.children) - 1 and len(node.children[index + 1].keys) > self.max_keys // 2:
            # Borrow from right sibling
            self.borrow_from_right(node, index)
        else:
            # Merge with sibling
            if index > 0:
                self.merge_with_left(node, index)
            else:
                self.merge_with_right(node, index)

    def borrow_from_left(self, node, index):
        child = node.children[index]
        left_sibling = node.children[index - 1]
        child.keys.insert(0, node.keys[index - 1])
        node.keys[index - 1] = left_sibling.keys.pop()
        if not left_sibling.is_leaf:
            child.children.insert(0, left_sibling.children.pop())

    def borrow_from_right(self, node, index):
        child = node.children[index]
        right_sibling = node.children[index + 1]
        child.keys.append(node.keys[index])
        node.keys[index] = right_sibling.keys.pop(0)
        if not right_sibling.is_leaf:
            child.children.append(right_sibling.children.pop(0))

    def merge_with_left(self, node, index):
        child = node.children[index]
        left_sibling = node.children[index - 1]
        left_sibling.keys.append(node.keys.pop(index - 1))
        node.children.pop(index)
        left_sibling.keys.extend(child.keys)
        left_sibling.children.extend(child.children)

    def merge_with_right(self, node, index):
        child = node.children[index]
        right_sibling = node.children[index + 1]
        child.keys.append(node.keys.pop(index))
        node.children.pop(index + 1)
        child.keys.extend(right_sibling.keys)
        child.children.extend(right_sibling.children)


    def list_records(self):
        def traverse(node):
            if node.is_leaf:
                return [(key, record) for key, record in zip(node.keys, node.children)]
            else:
                records = []
                for child in node.children:
                    records.extend(traverse(child))
                return records

        return traverse(self.root)
def load_tree(relation_dir):
    index_file = os.path.join(relation_dir, 'index.pkl')
    if os.path.exists(index_file):
        with open(index_file, 'rb') as f:
            return pickle.load(f)
    return BPlusTree()

def save_tree(tree, relation_dir):
    index_file = os.path.join(relation_dir, 'index.pkl')
    with open(index_file, 'wb') as f:
        #print("saving tree")
        pickle.dump(tree, f)

def is_page_full(page_file, max_records_per_page):
    with open(page_file, 'rb') as f:
        records = pickle.load(f)
    return len(records) >= max_records_per_page

def insert_record(relation_dir, key, record):
    print("inserting key : ", key)
    tree = load_tree(relation_dir)
    #searching the tree to prevent duplicate keys
    if tree.search(key):
        print("Key already exists", key)
        return False
    page_count = len([f for f in os.listdir(relation_dir) if f.startswith('page')])
    page_file = os.path.join(relation_dir, f'page{page_count}.dat')

    if not os.path.exists(page_file) or is_page_full(page_file, 10): #10 is the max number of records per page
        page_count += 1
        page_file = os.path.join(relation_dir, f'page{page_count}.dat')
        with open(page_file, 'wb') as f:
            pickle.dump([], f)

    with open(page_file, 'rb') as f:
        records = pickle.load(f)
    """
    if any(record[0] == key for record in records): #if the key already exists, do not insert
        return False
        """
    
    records.append((key, record))
    with open(page_file, 'wb') as f:
        pickle.dump(records, f)
    print("inserting record into tree: ", (key, record))
    tree.insert(key, (page_count, len(records) - 1)) #insert the key and the pointer to the record in the B+ Tree
    save_tree(tree, relation_dir) 
    return True

def search_record(relation_dir, key):
    tree = load_tree(relation_dir)
    result = tree.search(key)
    if result:
        #print("found the guy in the tree")
        page_number, record_index = result #find the page number and record index of the searched record 
        #print("page number: ", page_number, "record index: ", record_index, "key: ", key)
        page_file = os.path.join(relation_dir, f'page{page_number}.dat')
        with open(page_file, 'rb') as f:
            records = pickle.load(f)
        file_path = os.path.join(relation_dir, 'output.txt')
        with open(file_path, 'a') as f:
            #wrote the searched record to the file
            f.write(f"""Searched record: with index {record_index} \n""")
            f.close()
        return records[record_index] #bug: after deletion this index becomes out of range
    return None

def delete_record(relation_dir, key):
    tree = load_tree(relation_dir)
    result = tree.search(key)
    if result:
        page_number, record_index = result #deleted records page and index info 
        page_file = os.path.join(relation_dir, f'page{page_number}.dat')
        with open(page_file, 'rb') as f:
            records = pickle.load(f)
        del records[record_index] #delete from pickle file 
        with open(__file__, 'a') as f:
            #wrote the deleted record to the file
            file_path = os.path.join(relation_dir, 'output.txt')
            with open(file_path, 'a') as f:
                f.write(f"""Deleted record: with index {record_index} \n""")
                f.close()
        with open(page_file, 'wb') as f:
            pickle.dump(records, f) 
        tree.delete(key)
        # Update the record pointers in the B+ Tree
        records=pickle.load(open(page_file, 'rb')) #load the records from the page file again because it has changed 
        for i in range(record_index, len(records)): 
            updated_pointer = (page_number, i) #pointer points to page number and record index
            record_key = records[i][0] 
            tree.delete(record_key)  # first delete the old pointer to the record in that page
            save_tree(tree, relation_dir)
            print("updated pointer: ", updated_pointer)
            tree.insert(record_key, updated_pointer)  # insert the updated pointer to the record in that page
        
        save_tree(tree, relation_dir)
        return True
    return False
def list_all_records(relation_dir): #for me, to list the records in the relation
    tree = load_tree(relation_dir)
    record_pointers = tree.list_records()
    records = []
    for key, (page_number, record_index) in record_pointers:
        page_file = os.path.join(relation_dir, f'page{page_number}.dat')
        with open(page_file, 'rb') as f:
            page_records = pickle.load(f)
        records.append(page_records[record_index])
    return records

def get_schema(relation_dir):
    with open(os.path.join(relation_dir, 'schema.txt'), 'r') as f:
        schema = f.read().strip().split()
    return schema

if __name__ == "__main__":
    operation = sys.argv[1]
    relation_dir = os.path.dirname(__file__)
    schema = get_schema(relation_dir)
    primary_key_index = int(schema[1])-1 
    primary_key_type = schema[3 + 2 * int(primary_key_index)]
    print("Operation : ", operation)
    print("Primary key type : ", primary_key_type , "Primary key index: ", primary_key_index)
    record = sys.argv[2:]
    print("record: ", record)
    record = sys.argv[2:]
    print("record: ", record)
    if operation == "create_record":
        #primary_key_value = sys.argv[2]
        primary_key_value = record[primary_key_index]
        if primary_key_type == 'int':
            primary_key_value = int(primary_key_value) #böyle yapmazsak string comparison yapıyor,search yanlış dönüyor 
            
        
        print("primary key value: ", primary_key_value) #records indexth index must be the key stated in schema 
        success = insert_record(relation_dir, primary_key_value, record)
        sys.exit(0 if success else 1)
    elif operation == "search_record":
        primary_key_value=record[0]
        if primary_key_type == 'int':
            primary_key_value = int(primary_key_value)
            
        #records first index must be the key stated in schema
        
        print("primary key value for search: ", primary_key_value)
        record = search_record(relation_dir, primary_key_value)
        if record:
            #print(record) #TODO: to be written to output file
            #file is already open by another process
            output_file = open('output.txt', 'a')   
            output_file.write(str(record)+ '\n')

            output_file.close() #there are also other processes that are using the file
            sys.exit(0)
        else:
            sys.exit(1)
    elif operation == "delete_record":
        primary_key_value=record[0]
        if primary_key_type == 'int':
            primary_key_value = int(primary_key_value)
            
        
        print("primary key value for delete: ", primary_key_value)
        success = delete_record(relation_dir, primary_key_value)
        sys.exit(0 if success else 1)
    elif operation == "list_records": #for me, to list all records in the relation
        print("Listing all records...")
        records = list_all_records(relation_dir)
        for record in records:
            print(record)
        sys.exit(0)
    
    else:
        sys.exit(1)
