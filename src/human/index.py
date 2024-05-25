import os
import pickle
import sys

class BPlusTreeNode:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []

class BPlusTree:
    def __init__(self, max_keys=4):
        self.root = BPlusTreeNode()
        self.max_keys = max_keys

    def search(self, key):
        current_node = self.root
        while not current_node.is_leaf:
            i = 0
            while i < len(current_node.keys) and key >= current_node.keys[i]:
                i += 1
            current_node = current_node.children[i]

        for i, item in enumerate(current_node.keys):
            if item == key:
                return current_node.children[i]
        return None

    def insert(self, key, record_pointer):
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
                node.keys[i+1] = node.keys[i]
                node.children[i+1] = node.children[i]
                i -= 1
            node.keys[i+1] = key
            node.children[i+1] = record_pointer
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
        parent.keys.insert(index, child.keys[mid])
        parent.children.insert(index + 1, new_node)

        new_node.keys = child.keys[mid + 1:]
        new_node.children = child.children[mid + 1:]

        child.keys = child.keys[:mid]
        child.children = child.children[:mid + 1]

    def delete(self, key):
        # Implement the deletion logic
        pass

def load_tree(relation_dir):
    index_file = os.path.join(relation_dir, 'index.pkl')
    if os.path.exists(index_file):
        with open(index_file, 'rb') as f:
            return pickle.load(f)
    return BPlusTree()

def save_tree(tree, relation_dir):
    index_file = os.path.join(relation_dir, 'index.pkl')
    with open(index_file, 'wb') as f:
        pickle.dump(tree, f)

def is_page_full(page_file, max_records_per_page):
    with open(page_file, 'rb') as f:
        records = pickle.load(f)
    return len(records) >= max_records_per_page

def insert_record(relation_dir, key, record):
    tree = load_tree(relation_dir)
    page_count = len([f for f in os.listdir(relation_dir) if f.startswith('page')])
    page_file = os.path.join(relation_dir, f'page{page_count}.dat')

    if not os.path.exists(page_file) or is_page_full(page_file, 10):
        page_count += 1
        page_file = os.path.join(relation_dir, f'page{page_count}.dat')
        with open(page_file, 'wb') as f:
            pickle.dump([], f)

    with open(page_file, 'rb') as f:
        records = pickle.load(f)

    if any(record[0] == key for record in records):
        return False

    records.append((key, record))
    with open(page_file, 'wb') as f:
        pickle.dump(records, f)

    tree.insert(key, (page_count, len(records) - 1))
    save_tree(tree, relation_dir)
    return True

def search_record(relation_dir, key):
    tree = load_tree(relation_dir)
    result = tree.search(key)
    if result:
        page_number, record_index = result
        page_file = os.path.join(relation_dir, f'page{page_number}.dat')
        with open(page_file, 'rb') as f:
            records = pickle.load(f)
        return records[record_index]
    return None

def delete_record(relation_dir, key):
    tree = load_tree(relation_dir)
    result = tree.search(key)
    if result:
        page_number, record_index = result
        page_file = os.path.join(relation_dir, f'page{page_number}.dat')
        with open(page_file, 'rb') as f:
            records = pickle.load(f)
        del records[record_index]
        with open(page_file, 'wb') as f:
            pickle.dump(records, f)
        tree.delete(key)
        save_tree(tree, relation_dir)
        return True
    return False

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
    print("Primary key type : ", primary_key_type , "Primary key index: ", primary_key_index)

    if operation == "create_record":
        primary_key_value = sys.argv[2]
        if primary_key_type == 'int':
            primary_key_value = int(primary_key_value)
        record = sys.argv[2:]
        success = insert_record(relation_dir, primary_key_value, record)
        sys.exit(0 if success else 1)
    elif operation == "search_record":
        primary_key_value = sys.argv[2]
        if primary_key_type == 'int':
            primary_key_value = int(primary_key_value)
        record = search_record(relation_dir, primary_key_value)
        if record:
            print(record)
            sys.exit(0)
        else:
            sys.exit(1)
    elif operation == "delete_record":
        primary_key_value = sys.argv[2]
        if primary_key_type == 'int':
            primary_key_value = int(primary_key_value)
        success = delete_record(relation_dir, primary_key_value)
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)
