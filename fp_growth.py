import logging
import pandas as pd
import numpy as np
import csv
from fp_tree_node import *
from fp_growth import *
from collections import defaultdict

# Setting up a logger
logger = logging.getLogger()  # Initiating a logger
logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger.setLevel(logging.DEBUG)

def conditional_pattern_base(fp_tree, itemlist_retrieved,minimum_support):
    """
    Algo for conditional pattern base
    
    """
    # Fetching items from header table and the corresponding nodes that are linked to the item fetched from header table
    for header_item, corresponding_nodes in fp_tree.fetch_items():
        current_support_value = sum(node.count for node in corresponding_nodes)
        
        # Checking whether the current support value of the node is greater or equal to the minimum support
        # Also Need to check whether the item is already retrieved or not  
        if current_support_value >= minimum_support and header_item not in itemlist_retrieved:
            frequent_itemsets = [header_item] + itemlist_retrieved             
            # Returning frequent_itemsets
            yield (frequent_itemsets,current_support_value)
            
            # Now, we need to traverse through the nodes of the present itemset
            path_of_parents = fp_tree.fetch_parent_paths(header_item)
            
            # Once the path of parents are fetched for the present item, we need to create a new conditional FP tree based on the nodes present in the path of parents
            conditional_fp_tree = FPTree()
            conditional_item = None
            
            # We have to add nodes to this conditional FP tree 
            for current_parent_path in path_of_parents:
                # Setting the last item in the current parent path as the conditional item. Conditional item should not be None
                if conditional_item is None:
                    conditional_item = current_parent_path[-1].item
                
                conditional_fp_tree_iterator = conditional_fp_tree.get_root
                
                # Now using this iterator we traverse the conditional FP tree 
                for node in current_parent_path:
                    
                    # Checking whether the node is already present in the conditional FP Tree 
                    present_item = conditional_fp_tree_iterator.find_node(node.item)
                    
                    # If the node is already present in the conditional FP Tree we move the iterator to the present_item and repeat the process till the present_item is None
                    if present_item: 
                        conditional_fp_tree_iterator = present_item
                        continue
                    
                    # If the node is not present in the FP tree, a new node is created and added to the FP tree 
                    else:
                        
                        # Initializing the count of this new node as 0
                        count_of_new_node = 0
                        if node.item == conditional_item:
                            count_of_new_node = node.count
                        
                        # Creating this new node using fp_tree_node class
                        present_item = fp_tree_node(conditional_fp_tree,node.item,count_of_new_node)
                        conditional_fp_tree_iterator.add_node(present_item)
                        
                        # Now this node has to be updated in the header table
                        conditional_fp_tree.add_to_header_table(present_item)
                    
                    # After adding the node to the Header table, initiliazing the conditional fp tree iterator to the present item node    
                    conditional_fp_tree_iterator = present_item
                    
            # Once the conditional fp tree is generated, mining for frequent items starts
            for current_parent_path in conditional_fp_tree.fetch_parent_paths(conditional_item):
                current_node_in_parent_path = current_parent_path[-1]
                current_support_value = current_node_in_parent_path.count
                for node in reversed(current_parent_path[:-1]):
                    node.count += current_support_value     
            
            for frequent_item_sets in conditional_pattern_base(conditional_fp_tree,frequent_itemsets,minimum_support):
                yield frequent_item_sets
                
                
def mine_frequent_itemsets(transactions,threshold):
    
    # Initializing a default dictionary which assigns a value 0 if that key is not present in the dict
    itemset = defaultdict(lambda:0)

    # Calculating count of attributes from transactional data and storing them in itemset
    for transaction in transactions:
        for attribute in transaction:
            if attribute is not None:
                itemset[attribute] += 1
    
    logger.info("---------------Count of Items stored in a Dictionary---------------")
    # Sorting the itemsets in decreasing order of their count
    try:
        itemset=dict(sorted(itemset.items(), key=lambda item:item[1],reverse=True))
    except Exception as e:
        logger.error(e)
    
    logger.info("---------------Itemset sorted in decreasing order of their count---------------")    
    
    # Now we have to rearrange the items present in each transaction in the same way the itemsets are arranged
    try:
        for index, transaction in enumerate(transactions):
            transactions[index] = sorted(transaction,key=lambda x:itemset[x],reverse=True)
    except Exception as e:
        logger.error(e)
        
    logger.info("---------------Items in each transaction are sorted---------------")
    
    # It is time to build the FP Tree using the items present in the ordered transaction in transactional data
    fp_tree = FPTree()
    try:
        for transaction in transactions:
            if len(transaction) != 0:
                fp_tree.add_items(transaction)
    except Exception as e:
        return e
    
    logger.info("---------------FP Tree created---------------")
    
    # Now we have to mine the frequent patterns from the FP tree that was created using the items from the transaction data
    
    for frequent_itemsets in conditional_pattern_base(fp_tree,[],threshold):
        yield frequent_itemsets
    
    
    
        
    