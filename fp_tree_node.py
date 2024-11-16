from collections import namedtuple

class fp_tree_node(object):
    def __init__(self,tree,item,count=1):
        """
        -This is a constructor class used to define the node in an FP Tree.
        -Parameters passed:
            -item : Name of the item present in a transaction.
            -count : Number of occurences of that item.
        -Definitions: 
            -parent : Link to parent of the current node .
            -children : Link to children of the current node.
            -next_pointer : Link to the same item present in another branch.
        """
        self.tree=tree
        self.item=item # data point is item
        self.count=count
        self.parent=None
        self.children={}
        self.next_pointer=None        
    
    def find_node(self,item):
        """
        Function to find the node in which the item is present. 
        -Returns corresponding node of the item passed. 
        -Parameters Passed: 
            -item: An item is passed to find it in the child branch.
        """
        try:
            return self.children[item]
        except:
            return None
    
    @property
    def get_children(self):
        """
        Function to get the item from FP Tree node
        """
        return tuple(self.children.values())
        
    def print_node(self):
        """
        Function to print FP tree nodes and its values 
        """
        print(self.item, self.count)
        for child in self.children.keys():
            self.children[child].print_node()
            
    def print_leaves(self):
        """
        Function to print FP tree leaves and its values 
        """
        if len(self.children.keys()) == 0:
            print(self.item, self.count)
        
        for child in self.children.keys():
            self.children[child].print_leaves()
            
    def add_node(self,node):
        """
        Function to add a node to a parent
        -Parameters passed:
            -item : An item is passed as a node
        """
        if node.item not in self.children:
            self.children[node.item] = node
            node.parent = self
    
    @property
    def check_root(self):
        """
        Function to check for branches in an FP Tree
        """
        return self.item is None and self.count is None
        
class FPTree(object):
    def __init__(self):
        """
        1. Creating a root node for the FP tree with NULL value.
        2. Creating an empty header table
        """
        self.root = fp_tree_node(self, None, None)
        self.header = {}
    
    def print_tree(self):
        """
        Function to print nodes present in the FP Tree
        """
        root_node = self.root
        root_node.print_leaves()
        
    def fetch_nodes(self, item):
        """
        Function to fetch the nodes from the FP tree of the item in header table
        """
        # Accessing first node from the header table 
        node = self.header[item][0]
        if node is None:
            return KeyError
        while node is not None:
            yield node
            node = node.next_pointer
                
    def add_items(self, transaction):
        """
        Funtion to add items present in a transaction to the FP tree
        Parameters passed: 
            -transaction : ordered transaction
        Functionality:
            1. Take each item from the transaction.
            2. Check whether the item exists in the FP tree
                a. If exists -> Increment count of the node by 1.
                b. Does not exist -> Create a new node of the item and add the item with the count of 1 to the FP tree.
                 
        """
        current_node = self.root
        for item in transaction:
            next_node = current_node.find_node(item)
            if next_node is None:
                next_node = fp_tree_node(self,item)
                current_node.add_node(next_node)
                self.add_to_header_table(next_node)
            else:
                next_node.count += 1
            current_node = next_node
        
            
    def fetch_items(self):
        """
        Function to return items in the header table and its corresponding nodes
        Using yield instead of return to use fetch_items function as a generator so as to store local variables(not executing the function with a return)
        """
        for item in self.header.keys():
            yield item, self.fetch_nodes(item)

    def fetch_parent_paths(self, item):
        """
        Function to fetch the parent paths of the present item.
        """
        parent_paths = []  # Use a list to store multiple parent paths
        for node in self.fetch_nodes(item):
            current_parent_path_of_present_node = []
            while node and not node.check_root:
                current_parent_path_of_present_node.append(node)
                node = node.parent

            # Reverse the parent path to get the correct order
            current_parent_path_of_present_node.reverse()
            parent_paths.append(current_parent_path_of_present_node)

        return parent_paths  # Return a list of parent paths
    
    Item_Track = namedtuple("Item_Track", "begin end")
    def add_to_header_table(self,present_item):
        """
        Function to add items to the header table which are connected to the FP Tree
        Paramters passed:
            -present_item: Present node in the FP Tree
        """
        present_node = present_item.item
        try:
            # Path to the present_item 
            present_path = self.header[present_item.item]
            present_path[1].next_pointer = present_item
            self.header[present_item.item] = self.Item_Track(present_path[0], present_item)
        except:
            self.header[present_item.item] = self.Item_Track(present_item, present_item)
    
    @property        
    def get_root(self):
        return self.root