from browser.cdp_client import CDPClient
import webbrowser
import time
import subprocess

class YouTubeTool:

    AI_FUNCTIONS = {

        "search_query":
            "Search YouTube for videos.",

        "play_first":
            "Play the first video from the current search results.",

        "play_visible_video":
            "Play a currently visible video.",

        "pause":
            "Pause the current video.",

        "resume":
            "Resume the current video.",

        "skip_forward":
            "Skip forward in the current video.",

        "skip_backward":
            "Skip backward in the current video.",

        "skip_ad":
            "Skip an advertisement if possible.",

        "set_volume":
            "Set the playback volume.",

        "increase_volume":
            "Increase the playback volume.",

        "decrease_volume":
            "Decrease the playback volume.",

        "search":
            "Search YouTube using the browser search interface.",

        "exit_video":
            "Exit the current video.",

        "scroll_videos":
            "Scroll through the list of videos."
    }


    def __init__(self):
        self.client = CDPClient()
        self.client.connect()

    @staticmethod
    def open():
        user_profile_dir = "/home/varshith-nakirikanti/snap/chromium/common/chromium"

        subprocess.Popen([
            "chromium",
            "--remote-debugging-port=9222",
            "--remote-allow-origins=*",
            f"--user-data-dir={user_profile_dir}",
            "https://youtube.com"
        ])

        return "YouTube Opened"

    def skip_ad(self):
        """Locates the coordinates of the active skip ad button and performs a native hardware click."""
        coords_script = """
        (() => {
            const mainSkipSelectors = [
                '.ytp-skip-ad-button-modern',
                '.ytp-skip-ad-button',
                '.ytp-ad-skip-button-modern',
                '.ytp-ad-skip-button'
            ];
            
            const player = document.querySelector('.html5-video-player');
            if (player && !player.classList.contains('ad-showing')) {
                return "AD_ENDED_NATURALLY";
            }

            for (const selector of mainSkipSelectors) {
                const btn = document.querySelector(selector);
                if (btn) {
                    const style = window.getComputedStyle(btn);
                    if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                        if (btn.offsetHeight > 0 && btn.offsetWidth > 0) {
                            const rect = btn.getBoundingClientRect();
                            return {
                                x: Math.round(rect.left + rect.width / 2),
                                y: Math.round(rect.top + rect.height / 2)
                            };
                        }
                    }
                }
            }
            return "STILL_COUNTING_DOWN";
        })()
        """
        
        max_wait_time = 45
        start_time = time.time()
        coords = None
        
        while (time.time() - start_time) < max_wait_time:
            loop_res = self.client.send("Runtime.evaluate", {"expression": coords_script, "returnByValue": True})
            status = loop_res.get("result", {}).get("result", {}) or {}
            val = status.get("value")
            
            if isinstance(val, dict) and "x" in val:
                coords = val
                break
            elif val == "AD_ENDED_NATURALLY":
                return "AD_CONCLUDED_WITHOUT_CLICK"
                
            time.sleep(1.0)
        else:
            return "SKIP_AD_TIMEOUT"

        # Dispatch native hardware click actions sequence
        self.client.send("Runtime.evaluate", {"expression": "window.focus();"})
        
        self.client.send("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": coords["x"],
            "y": coords["y"],
            "button": "left",
            "clickCount": 1
        })
        time.sleep(0.1)
        self.client.send("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": coords["x"],
            "y": coords["y"],
            "button": "left",
            "clickCount": 1
        })

        # Anti-Pause check: Make sure the video keeps moving after the button clears
        time.sleep(0.5)
        force_play_script = """
        (() => {
            const video = document.querySelector('video');
            if (video && video.paused) {
                video.play();
                return "FORCED_PLAYBACK";
            }
            return "ALREADY_PLAYING";
        })()
        """
        self.client.send("Runtime.evaluate", {"expression": force_play_script, "returnByValue": True})
        return "AD_SKIPPED_SUCCESSFULLY"

    def pause(self):
        return self.client.send(
            "Runtime.evaluate",
            {
                "expression": """
                (() => {
                    const video = document.querySelector('video');
                    if (!video) return "NOT_FOUND";
                    video.pause();
                    return "PAUSED";
                })()
                """,
                "returnByValue": True
            }
        )
    
    def resume(self):
        return self.client.send(
            "Runtime.evaluate",
            {
                "expression": """
                (() => {
                    const video = document.querySelector('video');
                    if (!video) return "NOT_FOUND";
                    video.play();
                    return "PLAYING";
                })()
                """,
                "returnByValue": True
            }
        )
    
    def get_title(self):
        return self.client.execute_js("document.title")

    def search(self, query):
        js = f"""
        (() => {{
            const input = document.querySelector('input[name="search_query"]');
            if (!input) return "SEARCH_BOX_NOT_FOUND";

            input.focus();
            input.value = "{query}";

            input.dispatchEvent(
                new InputEvent(
                    "input",
                    {{ bubbles: true, composed: true }}
                )
            );

            input.dispatchEvent(
                new KeyboardEvent(
                    "keydown",
                    {{
                        key: "Enter",
                        code: "Enter",
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    }}
                )
            );

            return "SEARCH_TRIGGERED";
        }})()
        """
        return self.client.send(
            "Runtime.evaluate",
            {
                "expression": js,
                "returnByValue": True
            }
        )

    def play_first(self):
        nav_result = self.client.send(
            "Runtime.evaluate",
            {
                "expression": """
                (() => {
                    const firstVideo = document.querySelector(
                        'ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title-link, ytd-grid-video-renderer a#video-title'
                    );
                    if (!firstVideo) return "VIDEO_NOT_FOUND";
                    firstVideo.click();
                    return firstVideo.href;
                })()
                """,
                "returnByValue": True
            }
        )

        val = nav_result.get("result", {}).get("result", {}).get("value", "")
        if val == "VIDEO_NOT_FOUND":
            return "VIDEO_NOT_FOUND"

        return f"Navigated to video link successfully."
    
    def subscribe(self):
        """Finds and clicks the subscribe button on the current video page."""
        js_script = """
        (() => {
            const subscribeButton = document.querySelector(
                'ytd-subscribe-button-renderer button, #subscribe-button button'
            );
            
            if (!subscribeButton) return "SUBSCRIBE_BUTTON_NOT_FOUND";
            
            const text = subscribeButton.textContent.toLowerCase();
            if (text.includes("subscribed") || subscribeButton.hasAttribute('subscribed')) {
                return "ALREADY_SUBSCRIBED";
            }
            
            subscribeButton.click();
            return "SUBSCRIBE_CLICKED";
        })()
        """
        return self.client.send(
            "Runtime.evaluate",
            {
                "expression": js_script,
                "returnByValue": True
            }
        )
    
    def comment(self, text: str):
        """Scrolls down, targets the coordinates of the placeholder, types text via hardware keys, submits, waits 1s, and scrolls back up."""
        scroll_script = """
        (() => {
            const commentsHeader = document.querySelector('ytd-comments, #comments');
            if (commentsHeader) {
                commentsHeader.scrollIntoView({ block: "start", behavior: "instant" });
                window.scrollBy(0, -100);
                return "SCROLLED_TO_HEADER";
            }
            window.scrollTo(0, 400);
            return "SCROLLED_FALLBACK";
        })()
        """
        self.client.send("Runtime.evaluate", {"expression": scroll_script, "returnByValue": True})
        time.sleep(3)

        coords_script = """
        (() => {
            const box = document.querySelector('#simplebox-placeholder, #simple-box, ytd-comment-simplebox-renderer');
            if (!box) return null;
            
            const rect = box.getBoundingClientRect();
            return {
                x: Math.round(rect.left + rect.width / 2),
                y: Math.round(rect.top + rect.height / 2)
            };
        })()
        """
        coords_res = self.client.send("Runtime.evaluate", {"expression": coords_script, "returnByValue": True})
        coords = coords_res.get("result", {}).get("result", {}).get("value")
        
        if not coords or coords['y'] < 0:
            return "FAILED_COORDINATES_INVALID_OR_OFFSCREEN"
            
        self.client.send("Runtime.evaluate", {"expression": "window.focus();"})

        self.client.send("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": coords["x"],
            "y": coords["y"],
            "button": "left",
            "clickCount": 1
        })
        time.sleep(0.1)
        self.client.send("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": coords["x"],
            "y": coords["y"],
            "button": "left",
            "clickCount": 1
        })

        time.sleep(2.0)

        for char in text:
            self.client.send("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "text": char,
                "unmodifiedText": char
            })
            self.client.send("Input.dispatchKeyEvent", {
                "type": "keyUp"
            })
            time.sleep(0.02)
            
        time.sleep(1.5)

        self.client.send("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "modifiers": 2,
            "windowsVirtualKeyCode": 17,
            "code": "ControlLeft",
            "key": "Control"
        })
        
        self.client.send("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "modifiers": 2,
            "text": "\r",
            "unmodifiedText": "\r",
            "windowsVirtualKeyCode": 13,
            "code": "Enter",
            "key": "Enter"
        })
        self.client.send("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "modifiers": 2,
            "windowsVirtualKeyCode": 13,
            "code": "Enter",
            "key": "Enter"
        })
        
        self.client.send("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "modifiers": 0,
            "windowsVirtualKeyCode": 17,
            "code": "ControlLeft",
            "key": "Control"
        })

        time.sleep(1.0)

        scroll_back_script = """
        (() => {
            const videoPlayer = document.querySelector('video, #movie_player');
            if (videoPlayer) {
                videoPlayer.scrollIntoView({ block: "center", behavior: "smooth" });
                return "SCROLLED_BACK_TO_VIDEO";
            }
            window.scrollTo(0, 0);
            return "SCROLLED_BACK_FALLBACK";
        })()
        """
        self.client.send("Runtime.evaluate", {"expression": scroll_back_script, "returnByValue": True})
        time.sleep(1.0)

        return "COMMENT_SUBMITTED_AND_RETURNED_TO_VIDEO"

    def like(self):
        """Finds and clicks the like button to like the current video."""
        js_script = """
        (() => {
            const likeBtn = document.querySelector(
                'ytd-watch-metadata ytd-like-button-renderer button[aria-label*="like this video"], ' +
                'ytd-video-primary-info-renderer ytd-like-button-renderer button[aria-label*="like this video"], ' +
                'button[aria-label*="like this video"]'
            );
            if (!likeBtn) return "LIKE_BUTTON_NOT_FOUND";
            
            if (likeBtn.getAttribute('aria-pressed') === 'true') {
                return "ALREADY_LIKED";
            }
            
            likeBtn.click();
            return "LIKE_BUTTON_CLICKED_SUCCESSFULLY";
        })()
        """
        res = self.client.send("Runtime.evaluate", {"expression": js_script, "returnByValue": True})
        return res.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")

    def remove_like(self):
        """Finds the like button and removes the like if it was previously set."""
        js_script = """
        (() => {
            const likeBtn = document.querySelector(
                'ytd-watch-metadata ytd-like-button-renderer button[aria-label*="like this video"], ' +
                'ytd-video-primary-info-renderer ytd-like-button-renderer button[aria-label*="like this video"], ' +
                'button[aria-label*="like this video"]'
            );
            if (!likeBtn) return "LIKE_BUTTON_NOT_FOUND";
            
            if (likeBtn.getAttribute('aria-pressed') === 'false' || !likeBtn.getAttribute('aria-pressed')) {
                return "VIDEO_NOT_LIKED_YET";
            }
            
            likeBtn.click();
            return "LIKE_REMOVED_SUCCESSFULLY";
        })()
        """
        res = self.client.send("Runtime.evaluate", {"expression": js_script, "returnByValue": True})
        return res.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")
    
    def skip_forward(self, seconds: int):
        """Jumps the video forward instantly by the specified number of seconds."""
        js_script = f"""
        (() => {{
            const video = document.querySelector('video');
            if (!video) return "VIDEO_ELEMENT_NOT_FOUND";
            
            let targetTime = video.currentTime + {seconds};
            if (targetTime > video.duration) targetTime = video.duration;
            
            video.currentTime = targetTime;
            
            if (video.paused) video.play();
            return "SKIPPED_FORWARD_" + {seconds} + "_SECONDS";
        }})()
        """
        return self.client.send("Runtime.evaluate", {"expression": js_script, "returnByValue": True})

    def skip_backward(self, seconds: int):
        """Jumps the video backward instantly by the specified number of seconds."""
        js_script = f"""
        (() => {{
            const video = document.querySelector('video');
            if (!video) return "VIDEO_ELEMENT_NOT_FOUND";
            
            let targetTime = video.currentTime - {seconds};
            if (targetTime < 0) targetTime = 0;
            
            video.currentTime = targetTime;
            
            if (video.paused) video.play();
            return "SKIPPED_BACKWARD_" + {seconds} + "_SECONDS";
        }})()
        """
        return self.client.send("Runtime.evaluate", {"expression": js_script, "returnByValue": True})
    
    def set_volume(self, percentage: int) -> str:
        """Sets the YouTube player volume to an absolute percentage (0-100)."""
        # Ensure the percentage bounds are safely within 0 and 100
        percentage = max(0, min(100, percentage))
        
        volume_script = f"""
        (() => {{
            const player = document.querySelector('#movie_player') || document.querySelector('.html5-video-player');
            if (!player) return "YOUTUBE_PLAYER_ELEMENT_NOT_FOUND";
            
            if (typeof player.setVolume === 'function') {{
                player.setVolume({percentage});
                if (typeof player.unMute === 'function') {{
                    player.unMute();
                }}
                return "SUCCESSFULLY_SET_VOLUME_TO_" + player.getVolume() + "_PERCENT";
            }}
            
            const video = document.querySelector('video');
            if (video) {{
                video.volume = {percentage / 100};
                return "FALLBACK_NATIVE_VOLUME_SET";
            }}
            
            return "COULD_NOT_ADJUST_VOLUME";
        }})()
        """
        res = self.client.send("Runtime.evaluate", {"expression": volume_script, "returnByValue": True})
        return res.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")

    def increase_volume(self, current_volume: int = 50, step: int = 15) -> str:
        """Increases the volume by a specified step value (Defaults to +15%)."""
        target = current_volume + step
        return self.set_volume(target)

    def decrease_volume(self, current_volume: int = 50, step: int = 15) -> str:
        """Decreases the volume by a specified step value (Defaults to -15%)."""
        target = current_volume - step
        return self.set_volume(target)
    
    def set_playback_speed(self, speed: float):
        """Modifies the video playback speed natively via JavaScript (e.g., 0.5, 1.0, 1.5, 2.0)."""
        js_script = f"""
        (() => {{
            const video = document.querySelector('video');
            if (!video) return "VIDEO_ELEMENT_NOT_FOUND";
            
            // Adjust the playback rate property natively
            video.playbackRate = {speed};
            
            return "SUCCESSFULLY_SET_SPEED_TO_" + video.playbackRate + "_X";
        }})()
        """
        response = self.client.send("Runtime.evaluate", {"expression": js_script, "returnByValue": True})
        return response.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")
    
    def set_video_quality(self, quality: str):
        """
        Dynamically modifies the YouTube stream quality overlay layout.
        Accepts specific tags: '144p', '240p', '360p', '480p', '720p', '1080p', etc.
        Also handles descriptive aliases: 'highest', 'lowest', 'max', 'min'.
        """
        # Normalize incoming format strings safely
        target_quality = str(quality).strip().lower()
        
        js_script = f"""
        (() => {{
            const settingsButton = document.querySelector('.ytp-settings-button');
            if (!settingsButton) return "SETTINGS_BUTTON_NOT_FOUND";
            
            // Toggle open the controls drawer view pane if not already exposed
            if (settingsButton.getAttribute('aria-expanded') !== 'true') {{
                settingsButton.click();
            }}
            
            setTimeout(() => {{
                const menuItems = Array.from(document.querySelectorAll('.ytp-menuitem'));
                const qualityMenu = menuItems.find(item => {{
                    const label = item.querySelector('.ytp-menuitem-label');
                    return label && (label.textContent.includes('Quality') || label.textContent.includes('Качество'));
                }});
                
                if (!qualityMenu) return "QUALITY_MENU_NOT_FOUND";
                qualityMenu.click();
                
                setTimeout(() => {{
                    const options = Array.from(document.querySelectorAll('.ytp-menuitem'));
                    
                    // Filter options matching numeric values followed by 'p' (e.g., 1080p, 480p)
                    const resOptions = options.filter(item => {{
                        const label = item.querySelector('.ytp-menuitem-label');
                        return label && /\\d+p/.test(label.textContent);
                    }});
                    
                    if (resOptions.length === 0) return "RESOLUTION_OPTIONS_NOT_FOUND";
                    
                    // Sort options numerically ascending order
                    resOptions.sort((a, b) => {{
                        const valA = parseInt(a.querySelector('.ytp-menuitem-label').textContent);
                        const valB = parseInt(b.querySelector('.ytp-menuitem-label').textContent);
                        return valA - valB;
                    }});
                    
                    let selectedOption = null;
                    const mode = '{target_quality}';
                    
                    if (mode === 'highest' || mode === 'max') {{
                        selectedOption = resOptions[resOptions.length - 1];
                    }} else if (mode === 'lowest' || mode === 'min') {{
                        selectedOption = resOptions[0];
                    }} else {{
                        // Match accurate resolution format matching user parameter target
                        selectedOption = resOptions.find(item => {{
                            const text = item.querySelector('.ytp-menuitem-label').textContent.toLowerCase();
                            return text.includes(mode);
                        }});
                    }}
                    
                    if (selectedOption) {{
                        const targetLabel = selectedOption.querySelector('.ytp-menuitem-label').textContent;
                        selectedOption.click();
                        return "SUCCESSFULLY_SET_QUALITY_TO_" + targetLabel;
                    }}
                    
                    return "SPECIFIED_RESOLUTION_NOT_AVAILABLE";
                }}, 300);
            }}, 300);
            
            return "EXECUTING_QUALITY_ADJUSTMENT_SEQUENCE";
        }})()
        """
        response = self.client.send("Runtime.evaluate", {"expression": js_script, "returnByValue": True})
        return response.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")
    
    def navigate_to_panel(self, panel_name: str):
        """
        Navigates directly to standard YouTube views using uniform layout URLs.
        Accepts panel names like: 'home', 'shorts', 'subscriptions', 'your channel', 
        'history', 'playlists', 'watch later', 'liked videos', or 'downloads'.
        """
        destinations = {
            "home": "https://www.youtube.com/",
            "shorts": "https://www.youtube.com/shorts",
            "subscriptions": "https://www.youtube.com/feed/subscriptions",
            "your channel": "https://www.youtube.com/feed/you",
            "history": "https://www.youtube.com/feed/history",
            "playlists": "https://www.youtube.com/feed/playlists",
            "watch later": "https://www.youtube.com/playlist?list=WL",
            "liked videos": "https://www.youtube.com/playlist?list=LL",
            "downloads": "https://www.youtube.com/feed/downloads"
        }
        
        target = str(panel_name).strip().lower()
        if target not in destinations:
            return f"UNKNOWN_PANEL_REQUESTED: {panel_name}"
            
        url = destinations[target]
        self.client.send("Runtime.evaluate", {"expression": f'window.location.href = "{url}";', "returnByValue": True})
        return f"NAVIGATING_TO_{target.upper()}"

    def open_notifications(self):
        """Triggers the notifications overlay tray via DOM interaction layer or creator route fallback."""
        js_notifications = """
        (() => {
            const notifyBtn = document.querySelector('button[aria-label="Notifications"], ytd-notification-topbar-button-renderer button');
            if (notifyBtn) {
                notifyBtn.click();
                return "SUCCESSFULLY_OPENED_NOTIFICATIONS_TRAY";
            }
            window.location.href = "https://www.youtube.com/dashboard?o=U";
            return "FALLBACK_ROUTING_TO_CREATOR_DASHBOARD";
        })()
        """
        response = self.client.send("Runtime.evaluate", {"expression": js_notifications, "returnByValue": True})
        return response.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")

    def search_query(self, query: str):
        """Instructs YouTube's search engine to directly execute and populate a specific text query string."""
        import urllib.parse
        encoded_query = urllib.parse.quote(str(query).strip())
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        self.client.send("Runtime.evaluate", {"expression": f'window.location.href = "{search_url}";', "returnByValue": True})
        return f"EXECUTING_SEARCH_FOR_{query.upper()}"
    
    def scroll_videos(self, direction: str, steps: int = 1):
        """
        Scrolls smoothly video-by-video down or up through the current search or feed layout grid.
        direction: 'down' or 'up'
        steps: number of video elements to traverse sequentially
        """
        # Ensure our class instance tracks an internal pointer index
        if not hasattr(self, '_current_scroll_index'):
            self._current_scroll_index = 0

        target_direction = str(direction).strip().lower()
        
        for _ in range(steps):
            if target_direction == "down":
                self._current_scroll_index += 1
            elif target_direction == "up":
                self._current_scroll_index = max(0, self._current_scroll_index - 1)
            else:
                return f"UNKNOWN_SCROLL_DIRECTION: {direction}"

            js_scroll = f"""
            ((targetIndex) => {{
                const videoCards = Array.from(document.querySelectorAll('ytd-video-renderer, ytd-rich-item-renderer, ytd-compact-video-renderer'));
                if (videoCards.length === 0 || targetIndex >= videoCards.length || targetIndex < 0) {{
                    return "INDEX_OUT_OF_BOUNDS";
                }}
                videoCards[targetIndex].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                return "SCROLLED_TO_" + targetIndex;
            }})({self._current_scroll_index})
            """
            self.client.send("Runtime.evaluate", {"expression": js_scroll, "returnByValue": True})
            import time
            time.sleep(1.5)  # Let smooth scrolling physical animation finish intermediate paths cleanly

        return f"SUCCESSFULLY_SCROLLED_{target_direction.upper()}_TO_INDEX_{self._current_scroll_index}"

    def play_visible_video(self):
        """Launches the video card item that is currently targeted/centered on the display view layer."""
        if not hasattr(self, '_current_scroll_index'):
            self._current_scroll_index = 0

        js_play = f"""
        ((targetIndex) => {{
            const videoCards = Array.from(document.querySelectorAll('ytd-video-renderer, ytd-rich-item-renderer, ytd-compact-video-renderer'));
            if (videoCards.length === 0 || targetIndex >= videoCards.length || targetIndex < 0) {{
                return "NO_ACTIVE_CARD_FOUND";
            }}
            const playLink = videoCards[targetIndex].querySelector('a#video-title, a#thumbnail, a.ytd-video-renderer');
            if (playLink) {{
                playLink.click();
                return "PLAYBACK_TRIGGERED";
            }}
            return "ANCHOR_NOT_FOUND";
        }})({self._current_scroll_index})
        """
        response = self.client.send("Runtime.evaluate", {"expression": js_play, "returnByValue": True})
        return response.get("result", {}).get("result", {}).get("value", "EXECUTION_ERROR")

    def exit_video(self):
        """Returns precisely one page backward in browser history layout context to exit the current video view."""
        self.client.send("Runtime.evaluate", {"expression": "window.history.back();", "returnByValue": True})
        return "EXITED_VIDEO_ONE_STEP_BACKWARD"
    
    def get_video_transcript(self) -> dict:
        """
        Captures the active YouTube video URL via CDP, extracts the transcript natively 
        using the modern API syntax, and writes it directly to data/yt_transcript.txt.
        Returns a lightweight status dictionary instead of a massive raw string.
        """
        import os
        import requests
        import urllib.parse
        from youtube_transcript_api import YouTubeTranscriptApi

        # 1. Connect to browser and capture active video URL
        try:
            tabs = requests.get("http://localhost:9222/json").json()
        except Exception as e:
            return {"status": "ERROR", "message": f"Unable to reach port 9222. ({e})"}

        target_tab = None
        for tab in tabs:
            if tab.get("type") == "page" and "youtube.com/watch" in tab.get("url", ""):
                target_tab = tab
                break

        if not target_tab:
            return {"status": "ERROR", "message": "No active YouTube video page detected."}

        video_url = target_tab.get("url")

        # 2. Extract the video ID
        try:
            parsed_url = urllib.parse.urlparse(video_url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get("v")[0]
        except Exception:
            return {"status": "ERROR", "message": "Could not parse video ID from the browser URL."}

        # 3. Fetch the transcript cleanly
        try:
            api = YouTubeTranscriptApi()
            fetched_transcript = api.fetch(video_id)
            raw_data = fetched_transcript.to_raw_data()
            full_transcript_text = " ".join([item["text"] for item in raw_data])
        except Exception as e:
            return {"status": "ERROR", "message": f"Transcript extraction failed: {e}"}

        # 4. Save to the file cache instead of passing giant strings back live
        try:
            os.makedirs("data", exist_ok=True)
            txt_path = "data/yt_transcript.txt"
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_transcript_text)
                
            return {
                "status": "SUCCESS",
                "message": f"Transcript safely captured and saved to storage file.",
                "saved_to": txt_path,
                "video_url": video_url
            }
        except Exception as e:
            return {"status": "ERROR", "message": f"Failed to cache data file to disk: {e}"}