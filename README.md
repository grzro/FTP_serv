# FTP_serv

This server is using low-level connection handling via sockets. Of course there are plenty of libraries which makes possible to build app like that faster and much more expanded, but main aim of creating this server is to get a good knowledge about File Trasnfer Protocol and how to use sockets in Python.

The way that serwer works is based on RFCs: 959, 2228, 2389

14.12.18
Total Commander and Firefox works fine. Fixed bug with spaces in directories names.
At this moment Google Chrome does not work due to a problem with PWD command.
TC and FF works with absolute file paths. Chrome works with relative ones. 
Server can not detect at this moment which way of filepath handling needs to be choosen,
there is a problem with PWD (Print Working Directory) because every client manage it on his own way.

13.12.18
Server works fine with Google Chrome and Mozilla Firefox.
It allows to list directory, change directory and to download file from the server.
For security reasons server forbids to use '../' and to move to the 'deeper' directory
than this where server files are.

Next task is to make it working with FTP clients like FileZilla or TotalCommander.
In further future I am planning to create a user validation mechanism.
