BROWSER_PROMPT = """
==================================================

2. browser

Functions:

* search

Arguments:

{
"query":"..."
}

* open_url

Arguments:

{
"url":"..."
}

* open_new_tab

Arguments:

{}

Functions:

* open_new_tab
* search
* open_website
* close_tab
* refresh
* go_back
* go_forward


Examples:

User:
Open new tab

Output:

{
"tool":"browser",
"function":"open_new_tab",
"arguments":{}
}

User:
Search youtube

Output:

{
"tool":"browser",
"function":"search",
"arguments":{
"query":"youtube"
}
}

Example 2:

User:
Close current tab

Output:

{
"tool":"browser",
"function":"close_tab",
"arguments":{}
}


User:
Refresh page

Output:

{
"tool":"browser",
"function":"refresh",
"arguments":{}
}

User:
Go back

Output:

{
"tool":"browser",
"function":"go_back",
"arguments":{}
}


=========================================
Example 3:

User:
Open chrome and then open youtube

Output:

{
  "steps":[
    {
      "tool":"app",
      "function":"open",
      "arguments":{
        "app":"chrome"
      }
    },
    {
      "tool":"browser",
      "function":"open_url",
      "arguments":{
        "url":"https://youtube.com"
      }
    }
  ]
}

"""