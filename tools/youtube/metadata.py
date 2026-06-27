TOOL_METADATA = {
    "name": "youtube",

    "description": (
        "Interact with YouTube to search, play and "
        "control videos."
    ),

    "functions": {

        "search_query": {

            "description":
                "Search YouTube for videos.",

            "arguments": {
                "query": "string"
            },

            "memory_resolution": {
                "query": None
            },

            "examples": [
                "play imagine dragons",
                "search youtube for python tutorials",
                "find relaxing music"
            ]
        },

        "search": {

            "description":
                "Search YouTube using the browser interface.",

            "arguments": {
                "query": "string"
            },

            "memory_resolution": {
                "query": None
            },

            "examples": [
                "search youtube for AI news"
            ]
        },

        "play_first": {

            "description":
                "Play the first video from the current search results.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "play first video"
            ]
        },

        "play_visible_video": {

            "description":
                "Play one of the currently visible videos.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "play this video"
            ]
        },

        "pause": {

            "description":
                "Pause the currently playing video.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "pause",
                "pause video"
            ]
        },

        "resume": {

            "description":
                "Resume the currently paused video.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "resume",
                "continue video"
            ]
        },

        "skip_forward": {

            "description":
                "Skip forward in the current video.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "skip ahead"
            ]
        },

        "skip_backward": {

            "description":
                "Skip backward in the current video.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "go back ten seconds"
            ]
        },

        "skip_ad": {

            "description":
                "Skip an advertisement when possible.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "skip ad"
            ]
        },

        "set_volume": {

            "description":
                "Set the playback volume.",

            "arguments": {
                "percentage": "integer"
            },

            "memory_resolution": {
                "percentage": None
            },

            "examples": [
                "set volume to 50 percent"
            ]
        },

        "increase_volume": {

            "description":
                "Increase the playback volume.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "increase volume"
            ]
        },

        "decrease_volume": {

            "description":
                "Decrease the playback volume.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "decrease volume"
            ]
        },

        "exit_video": {

            "description":
                "Exit the current video.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "close video"
            ]
        },

        "scroll_videos": {

            "description":
                "Scroll through the current list of videos.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "scroll down"
            ]
        }
    }
}