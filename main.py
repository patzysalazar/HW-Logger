# assignment tracker for school
from operator import index

import background
from flask import Flask, request
from pymongo import MongoClient

#client = MongoClient("mongodb+srv://ps_db_user:wuCnuEM2vyU1peBk@hwlogger-database.xh663fz.mongodb.net/?appName=hwLogger-database")  # local MongoDB
client = MongoClient("mongodb+srv://ps_db_user:wuCnuEM2vyU1peBk@hwlogger-database.xh663fz.mongodb.net/hwLoggerDB?retryWrites=true&w=majority")
db = client["hwLoggerDB"]
# database name
collection = db["assignments"]
print("MongoDB connected. Current assignments:")
for assignment in collection.find():
    print(assignment)

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def hwLogger():
    error = ""
    errorHTML = ""
    if request.method == "POST":
        if request.form.get("delete"):
            delete_index = int(request.form.get("delete"))

            # Reload assignments from MongoDB
            new_assignments = list(collection.find().sort("_id"))

            if 0 <= delete_index < len(new_assignments):
                assignment_id = new_assignments[delete_index]["_id"]
                collection.delete_one({"_id": assignment_id})
            #assignment_id = new_assignments[delete_index]["_id"]

            collection.delete_one({"_id": assignment_id})

        #if update
        elif request.form.getlist("completed"):

            # Reload assignments from MongoDB
            new_assignments = list(collection.find().sort("_id"))

            # Reset all assignments to not completed
            collection.update_many({}, {"$set": {"completed": False}})

            # Get checked boxes (these are indexes from your form)
            CheckBoxes = request.form.getlist("completed")

            # Turn checked ones to True
            for index in CheckBoxes:
                assignment_id = new_assignments[int(index)]["_id"]
                collection.update_one(
                    {"_id": assignment_id},
                    {"$set": {"completed": True}}
                )
        # request.form has all the data the browser sends to server
        #holds the data sent from an html form when method is post
        elif request.form.get("assignment_name"):
            AssignmentName = request.form.get("assignment_name").strip()
            AssignmentDetails = request.form.get("assignment_details").strip()
            DueDate = request.form.get("due_date").strip()

            # check if field empty
            if len(AssignmentName) == 0 or len(AssignmentDetails) == 0 or len(DueDate) == 0:
                error = "Error: fields must be full"
                errorHTML = f'<p style="color:red;">{error}</p>' if error else ""
            else:
                assignment = {
                    "Assignment Name": AssignmentName,
                    "Assignment Details" : AssignmentDetails,
                    "Due Date" : DueDate,
                    "completed" : False
                }
                result = collection.insert_one(assignment)
                print("Inserted ID:", result.inserted_id)

#handles get and post
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
        <title> HW Logger </title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Dancing+Script:wght@700&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                padding: 40px;
            }}

            h1 {{
                text-align: center;
            }}

            form {{
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                margin-bottom: 30px;
            }}

            input[type="text"] {{
                width: 100%;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ddd;
                margin-bottom: 15px;
            }}

            button {{
                padding: 8px 14px;
                border-radius: 10px;
                border: none;
                background: #4f46e5;
                color: white;
                cursor: pointer;
            }}
            .assignment-box {{
                background: #ffffff;
                padding: 15px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                }}
            .assignment-information {{
                flex-grow: 1;
                }}
            .assignment-information p {{
                margin: 4px 0;
                }}
            .assignment-actions button {{
                background: #ef4444; /* red delete button */
                color: white;
                border: none;
                border-radius: 10px;
                padding: 5px 10px;
                cursor: pointer;
                }}
            .assignment-actions button:hover {{
                opacity: 0.9;
                }}
            
    </style>
    </head>
    <body>
    
    
        <h1> Homework Logger </h1>
        
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script>
        $(document).ready(function() {{//run page after loading 
            // Handle Delete without reloading/refreshing the page
            $(document).on("click", ".delete", function(delt) {{
                delt.preventDefault(); // prevent form submit
                let index = $(this).val();//gets value
                $.post("/", {{delete: index}}, function() {{//]send post request to delete assignment
                    location.reload();//reloads page to current status
                }});
            }});
            
        }});
        </script>
        
     
        <form method="POST">
            <label for="assignment_name"> Assignment Name </label><br>
            <input type="text" id="assignment_name" name="assignment_name"><br><br>
            
            <label for="assignment_details"> Assignment Details </label><br>
            <input type="text" id="assignment_details" name="assignment_details"><br><br>
            
            <label for="due_date"> Due Date </label><br>
            <input type="text" id="due_date" name="due_date"><br><br>
            
            <!-- Button inside form tag, -->
            <button type="submit">Add Assignment</button>
            {errorHTML}
        </form>
        
    </body>
    </html>
    """
    #show in browser
    html = html + f"""
    <a id="assignmentsList"></a>
    <h2> List of Assignments </h2>
    <form method="POST" id="assignmentsForm">
    """
    new_assignments = list(collection.find().sort("_id"))
    for index, assignment in enumerate(new_assignments):
        checked = "checked" if assignment.get('completed', False) else ""
        html += f"""
        <div class="assignment-box">
            <div class="assignment-information">
                <p><strong>{assignment.get('Assignment Name', '')}</strong></p>
                <p>{assignment.get('Assignment Details', '')}</p>
                <p>{assignment.get('Due Date', '')}</p>
                <p><label><input type="checkbox" name="completed" value="{index}" {checked}>Completed</label></p>
            </div>
            <div class="assignment-actions">    
                <button type="submit" name="delete" value="{index}">Delete</button>
            </div>
        </div>
        """
    html = html + """
        <button type="submit">Update Completed</button>
    </form>
    """
    return html
app.run(host="0.0.0.0", port=5005, debug=True)


