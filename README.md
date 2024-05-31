Code straight from Claude, with minor tweaks. (We are doomed)

Upload a CSV file: curl -X POST -F 'file=@data.csv' http://localhost:5000/upload
or http://localhost:5000/upload in browser
Retrieve a row: http://localhost:5000/get?dataset=data.csv&column1=value1&column2=value2
Search rows: http://localhost:5000/search?dataset=data.csv&q=example