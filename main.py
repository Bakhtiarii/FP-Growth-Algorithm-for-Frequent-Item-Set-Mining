import os
import numpy as np
import matplotlib.pylab as plt
import csv
import logging
import time
import psutil
import tracemalloc
from fp_tree_node import *
from fp_growth import *
from plot_utils import *

# Setting up a logger
logger = logging.getLogger()  # Initiating a logger
logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger.setLevel(logging.DEBUG)


# To begin with FP growth Algorithm, first we need to fetch the transactional data

transactions = []  # Initiliazing a list to store the transactions from csv file

# For "Adults" dataset(https://archive.ics.uci.edu/dataset/2/adult) fetched from UCI benchmark datasets

input_datasets_path = [
    "datasets/Abalone/abalone.csv",
    "datasets/Adult/adult.csv",
    "datasets/Air-Quality/air-quality.csv",
    "datasets/Balance-scale/balance-scale.csv",
    "datasets/Breast-Cancer/breast_cancer.csv",
    "datasets/Comp-Hardware/comp-hardware.csv",
    "datasets/Glass/glass.csv",
    "datasets/Iris/iris.csv",
    "datasets/Liver-Disorder/liver-disorder.csv",
    "datasets/Metro-Traffic/metro-traffic.csv",
    "datasets/Online-Retail/online-retail.csv",
    "datasets/Sample/sample.csv",
    "datasets/Tic-Tac-Toe/tic-tac-toe.csv",
    "datasets/Voting/voting.csv",
    "datasets/Wine/wine.csv",
    "datasets/Zoo/zoo.csv"
]


# List of minimum support valeus to test FP Growth Algorithm
minimum_support_abalone = [100,600,1000,2000,2500]
minimum_support_adult = [100,700,1750,5000,10000]
minimum_support_airquality = [100,700,1750,5000,6000]
minimum_support_balancescale = [10,50,100,200,400]
minimum_support_breastcancer = [10,30,50,70,150]
minimum_support_computer_hardware = [10,20,30,50,75]
minimum_support_glass = [10,30,50,70,150]
minimum_support_iris = [10,30,50,70,100]
minimum_support_liverdisorder = [10,30,50,70,150]
minimum_support_metro_traffic = [100,700,1750,5000,10000]
minimum_support_onlineretail = [1000,10000,50000,200000,500000]
minimum_support_tictactoe = [10,100,300,600,800]
minimum_support_voting = [10,30,50,150,300]
minimum_support_wine = [10,30,50,70,150]
minimum_support_zoo = [10,30,50,70,90]
minimum_support_sample = [3]
minimum_supports = [minimum_support_abalone,minimum_support_adult,minimum_support_airquality,minimum_support_balancescale,minimum_support_breastcancer,
                    minimum_support_computer_hardware,minimum_support_glass,minimum_support_iris,minimum_support_liverdisorder,minimum_support_metro_traffic,
                    minimum_support_onlineretail,minimum_support_sample,minimum_support_tictactoe,minimum_support_voting,minimum_support_wine,
                    minimum_support_zoo]

count = 0
for input_dataset_path in input_datasets_path:
    minimum_support = minimum_supports[count]
    dataset_name = input_dataset_path.split("/")
    input_dataset_name = dataset_name[1]
    output_path = "outputs/" + input_dataset_name
    try:
        os.makedirs(output_path)
    except:
        pass     

    transactions = []
    # Reading input CSV dataset and converting it into transactional data
    logger.info("---------------Reading Input Data---------------")
    try:
        with open(input_dataset_path) as input_data:
            for row in csv.reader(input_data):
                transactions.append(row)
    except Exception as e:
        logger.error(e)
    logger.info("---------------Transactional Data formed---------------")

    """
    Upon manual inspection of the input data, there are several data entry points with unwanted characters such as "?" and single quotes('"')
    For missing data points, data points are stored as either ""(empty values) or "?" in the dataset which bring no value. 
    Hence it crucial to clean the data before using FP Growth algorith to mine frequent patterns.

    """
    logger.info("---------------Performing Data Cleaning---------------")
    try:
        for item in transactions:
            item = list(filter(lambda x: x != '', item))
            for i in item:
                if '?' in i:
                    item.remove(i)
                if '"' in i:
                    i = i.replace('"', '')
    except Exception as e:
        logger.error(e)

    logger.info("---------------Data Cleaning Complete---------------")

    # Finding maximum number of attributes present in the transactional dataset

    maximum_number_of_attributes = 0
    for transaction in transactions:
        if maximum_number_of_attributes < len(transaction):
            maximum_number_of_attributes = len(transaction)

    logger.info("Maximum number of attributes present in the dataset : %s",
                maximum_number_of_attributes)

    
    
    # Since we are running the algorithm multiple times, we are storing the time taken for the algorithm to complete and memory used for each threshold value for analysis
    time_taken = []
    memory_used = []
    total_number_of_frequent_itemsets = []
    for threshold in minimum_support:
        frequent_itemsets = []
        tracemalloc.start()
        start_time = time.time()
        for itemset, support in mine_frequent_itemsets(transactions, threshold):
            frequent_itemsets.append((itemset, support))
        
        end_time = time.time()
        memory_used.append(tracemalloc.get_traced_memory()[0])
        tracemalloc.stop()
        
        execution_time = end_time - start_time
        time_taken.append(round(execution_time*1000,3)) # Time in micro seconds rounded off to 3 digits 
        number_of_frequent_itemsets = len(frequent_itemsets)
        total_number_of_frequent_itemsets.append(number_of_frequent_itemsets)
        
        answer = sorted(frequent_itemsets,key= lambda x:x[1],reverse=True)
        with open(f"{output_path}/Frequent_Patterns_{threshold}.csv","w") as f:
            write = csv.writer(f)
            write.writerows(answer)
            
    # Plotting execution time against several minimum support values
    x_axis = np.arange(len(minimum_support))
    plt.bar(x_axis,time_taken,color="maroon",tick_label=minimum_support)
    xlabel = "Minimum Support Values"
    ylabel = "Execution Time(milli-seconds)"
    addlabels(x_axis,time_taken)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f"{output_path}/{ylabel}.png")
    plt.clf()

    # Plotting memory usage against several minimum support values
    x_axis = np.arange(len(minimum_support))
    plt.bar(x_axis,memory_used,color="green",tick_label=minimum_support)
    xlabel = "Minimum Support Values"
    ylabel = "Memory Usage(Bytes)"
    # addlabels(x_axis,memory_used)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f"{output_path}/{ylabel}.png")
    plt.clf()
    
    # Plotting number of frequent patterns generated against several minimum support values
    x_axis = np.arange(len(minimum_support))
    plt.bar(x_axis,total_number_of_frequent_itemsets,color="blue",tick_label=minimum_support)
    xlabel = "Minimum Support Values"
    ylabel = "Number of frequent patterns mined"
    addlabels(x_axis,total_number_of_frequent_itemsets)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f"{output_path}/{ylabel}.png")
    plt.clf()
    
    with open(f"{output_path}/Memory_taken.csv","w") as f:
        write = csv.writer(f)
        write.writerow(memory_used)
    
    with open(f"{output_path}/Execution_time.csv","w") as f:
        write = csv.writer(f)
        write.writerow(time_taken)
    
    count += 1

