# COMPX234-A3
This is the output of Server,py
(base) PS E:\System and Network\COMPX234-A3> python Server.py 51234
Server listening on port 51234...

This is sigle client
python Client.py localhost 51234 client_1.txt


This is mult-client
(base) PS E:\System and Network\COMPX234-A3> for ($i = 1; $i -le 10; $i++) {
>>     Start-Process python -ArgumentList "Client.py", "localhost", "51234", "client_$i.txt"
>> }

They all can run in powershell,everyone need new terminal.
