YOUTUBE_PROMPT = """
==================================================

7. youtube

Functions:

* search
* play_first
* pause
* resume
* get_title
* subscribe
* comment
* like
* remove_like
* skip_forward
* skip_backward
* skip_ad
* set_volume
* increase_volume
* decrease_volume
* set_playback_speed
* set_video_quality
* navigate_to_panel
* open_notifications
* search_query
* scroll_videos
* play_visible_video
* exit_video
* get_video_transcript

Arguments for get_video_transcript:
{} (No parameters required. The tool dynamically extracts the active YouTube video URL from the open browser session via CDP, safely caches the continuous text structure down onto disk storage space, and reports back a file handling success token.)

Arguments for scroll_videos:
{
  "direction": string ("down" or "up"),
  "steps": integer (optional, defaults to 1)
}

Arguments for navigate_to_panel:
{
  "panel_name": string ("home", "shorts", "subscriptions", "your channel", "history", "playlists", "watch later", "liked videos", "downloads")
}

Arguments for search_query:
{
  "query": string (e.g., "lofi hip hop radio", "python tutorials")
}

Arguments for set_video_quality:
{
  "quality": string (e.g., "144p", "360p", "720p", "1080p", "highest", "lowest")
}

Arguments for set_playback_speed:
{
  "speed": float (e.g., 1.5, 2.0, 1.0)
}

Arguments for comment:
{
  "text": "your comment string"
}

Arguments for skip_forward:
{
  "seconds": integer (Calculate total seconds. e.g., "30s" = 30, "1 min" = 60, "2 min 10s" = 130)
}

Arguments for skip_backward:
{
  "seconds": integer (Calculate total seconds. e.g., "50s" = 50, "3 min" = 180)
}

Arguments for skip_ad:
{}

Arguments for set_volume:
{
  "percentage": integer (0 to 100)
}

Arguments for increase_volume:
{
  "current_volume": integer (optional, defaults to 50),
  "step": integer (optional, defaults to 15)
}

Arguments for decrease_volume:
{
  "current_volume": integer (optional, defaults to 50),
  "step": integer (optional, defaults to 15)
}

IMPORTANT:

Use argument names EXACTLY as specified.

For comment:
{
  "text": "<comment>"
}

Never use:
{
  "comment": "<comment>"
}

Examples:

User:
Subscribe to this channel

Output:
{
"tool":"youtube",
"function":"subscribe",
"arguments":{}
}

User:
Comment nice video on youtube

Output:
{
"tool":"youtube",
"function":"comment",
"arguments":{
    "text": "nice video"
}
}

User:
Like this video

Output:
{
"tool":"youtube",
"function":"like",
"arguments":{}
}

User:
Give this video a thumbs up

Output:
{
"tool":"youtube",
"function":"like",
"arguments":{}
}

User:
Unlike this video

Output:
{
"tool":"youtube",
"function":"remove_like",
"arguments":{}
}

User:
Remove my like from this video

Output:
{
"tool":"youtube",
"function":"remove_like",
"arguments":{}
}

User:
Skip 30 seconds forward

Output:
{
"tool":"youtube",
"function":"skip_forward",
"arguments":{
    "seconds": 30
}
}

User:
Fast forward 3 minutes

Output:
{
"tool":"youtube",
"function":"skip_forward",
"arguments":{
    "seconds": 180
}
}

User:
Go back 50 seconds

Output:
{
"tool":"youtube",
"function":"skip_backward",
"arguments":{
    "seconds": 50
}
}

User:
Rewind 1 and a half minutes

Output:
{
"tool":"youtube",
"function":"skip_backward",
"arguments":{
    "seconds": 90
}
}

User:
Skip this ad

Output:
{
"tool":"youtube",
"function":"skip_ad",
"arguments":{}
}

User:
Clear the commercial breakdown

Output:
{
"tool":"youtube",
"function":"skip_ad",
"arguments":{}
}

User:
make it quieter

Output:
{
"tool":"youtube",
"function":"decrease_volume",
"arguments":{
    "step": 25
}
}

User:
turn down the sound a bit

Output:
{
"tool":"youtube",
"function":"decrease_volume",
"arguments":{
    "step": 15
}
}

User:
make it higher

Output:
{
"tool":"youtube",
"function":"increase_volume",
"arguments":{
    "step": 25
}
}

User:
turn up the volume

Output:
{
"tool":"youtube",
"function":"increase_volume",
"arguments":{
    "step": 15
}
}

User:
mute the video

Output:
{
"tool":"youtube",
"function":"set_volume",
"arguments":{
    "percentage": 0
}
}

User:
make it max volume

Output:
{
"tool":"youtube",
"function":"set_volume",
"arguments":{
    "percentage": 100
}
}

User:
set volume to 60 percent

Output:
{
"tool":"youtube",
"function":"set_volume",
"arguments":{
    "percentage": 60
}
}

User:
Watch this tutorial at 2x speed

Output:
{
  "tool": "youtube",
  "function": "set_playback_speed",
  "arguments": {
    "speed": 2.0
  }
}

User:
Change video resolution to 480p to save mobile data balance

Output:
{
  "tool": "youtube",
  "function": "set_video_quality",
  "arguments": {
    "quality": "480p"
  }
}

User:
Show me what channels I am subscribed to right now

Output:
{
  "tool": "youtube",
  "function": "navigate_to_panel",
  "arguments": {
    "panel_name": "subscriptions"
  }
}

User:
go down 3 videos

Output:
{
  "tool": "youtube",
  "function": "scroll_videos",
  "arguments": {
    "direction": "down",
    "steps": 3
  }
}

User:
play this video

Output:
{
  "tool": "youtube",
  "function": "play_visible_video",
  "arguments": {}
}

User:
exit the video

Output:
{
  "tool": "youtube",
  "function": "exit_video",
  "arguments": {}
}
User:
Can you summarize the video that is currently playing right now?

Output:
{
  "tool": "youtube",
  "function": "get_video_transcript",
  "arguments": {}
}

User:
Explain me this video in short

Output:
{
  "tool": "youtube",
  "function": "get_video_transcript",
  "arguments": {}
}

User:
Why did the speaker use that specific word in the video?

Output:
{
  "tool": "youtube",
  "function": "get_video_transcript",
  "arguments": {}
}

User:
What is this video talking about? Give me a long detailed explanation.

Output:
{
  "tool": "youtube",
  "function": "get_video_transcript",
  "arguments": {}
}

"""