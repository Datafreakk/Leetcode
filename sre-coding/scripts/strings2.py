from datetime import datetime 

logs = [
    "2024-01-15 14:30:00",      # already correct format
    "15/01/2024 14:30:00",      # DD/MM/YYYY
    "Jan 15 2024 14:30:00",     # Mon DD YYYY
    "01-15-2024 02:30 PM",      # MM-DD-YYYY 12hr
]

formats = [
     "%Y-%m-%d %H:%M:%S",
     "%d/%m/%Y %H:%M:%S",
     "%b %d %Y %H:%M:%S",
     "%m-%d-%Y %I:%M %p",
]

def strinparser(logs):
    for i in logs:
        for j in formats:
         try:
           dt = datetime.strptime(i,j)
           print(dt.strftime("%Y-%m-%d %H:%M:%S"))
           break
         except ValueError:
            continue
          

strinparser(logs)
        

