import pymongo
import matplotlib.pyplot as plt
import numpy as np

# connect to MongoDB database
client = pymongo.MongoClient("mongodb+srv://zyy0328:zyy98328@cluster0.9f4tolb.mongodb.net/?retryWrites=true&w=majority")

# select db and collection
db = client.chatbot
collection = db.user_commands

# count the number of different commands for every id
command_counts = {}
for doc in collection.find():
    id = doc['user_id']
    command = doc['command']
    if id in command_counts:
        command_counts[id][command] = command_counts[id].get(command, 0) + 1
    else:
        command_counts[id] = {command: 1}

# According to each id, generate bar charts corresponding to the number of command statistics
for id in command_counts:
    commands = list(command_counts[id].keys())
    counts = list(command_counts[id].values())
    x_pos = np.arange(len(commands))

    plt.bar(x_pos, counts, align='center', alpha=0.5)
    plt.xticks(x_pos, commands)
    plt.ylabel('Count')
    plt.title('Command Count for ID {}'.format(id))

    plt.show()
