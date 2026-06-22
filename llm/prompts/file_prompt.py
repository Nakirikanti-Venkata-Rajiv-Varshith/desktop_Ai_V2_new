FILE_PROMPT = """
==================================================

4. file

Functions:

* list_directory

Arguments:

{
"path":"..."
}

* read_file

Arguments:

{
"path":"..."
}

* create_folder

Arguments:

{
"path":"..."
}

Examples:

User:
Show files in Downloads

Output:

{
"tool":"file",
"function":"list_directory",
"arguments":{
"path":"~/Downloads"
}
}

User:
Read notes.txt

Output:

{
"tool":"file",
"function":"read_file",
"arguments":{
"path":"notes.txt"
}
}

User:
Create folder Projects

Output:

{
"tool":"file",
"function":"create_folder",
"arguments":{
"path":"Projects"
}
}
"""