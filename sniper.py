# Run "py -m pip install requests packaging" in command prompt before running the sniper for the first time, otherwise it will break the sniper.

import requests
import re
import urllib.parse
import webbrowser
import json
import shlex
import tkinter as tk
import os
import sys
import subprocess
import time
from packaging.version import parse as parse_version
from tkinter import scrolledtext
from datetime import datetime, timezone

# Configuration
USER_TOKEN = "ADD-DISCORD-TOKEN-HERE"
# Add multiple channel IDs to this list
CHANNEL_IDS = ["1506072605525016737"] 
HEADERS = {"Authorization": USER_TOKEN}
KEYWORDS = ["dreamspace", "cyberspace", "glitched", "glitch", "jester", "singularity"]
DISCORD_SESSION = "ADD-SESSION-TOKEN-HERE"
APP_VERSION = "1.0.0"
UPDATE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/your_script.py"
AUTO_UPDATE_ON_START = True

# Dictionary to track the last message ID for each channel
last_message_ids = {cid: None for cid in CHANNEL_IDS}

def get_remote_script():
    try:
        response = requests.get(UPDATE_URL, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None

def extract_version_from_script(script_text):
    if not script_text:
        return None

    match = re.search(r'^APP_VERSION\s*=\s*[\'"]([^\'"]+)[\'"]', script_text, re.MULTILINE)
    if match:
        return match.group(1)

    return None

def restart_script():
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    subprocess.Popen([python_exe, script_path])
    os._exit(0)

def apply_update(new_script_text, text_widget=None):
    try:
        script_path = os.path.abspath(sys.argv[0])
        backup_path = script_path + ".bak"
        temp_path = script_path + ".new"

        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(new_script_text)

        if os.path.exists(script_path):
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.replace(script_path, backup_path)

        os.replace(temp_path, script_path)

        if text_widget:
            log_message(text_widget, "Update installed successfully. Restarting...")
        restart_script()

    except Exception as e:
        if text_widget:
            log_message(text_widget, f"Update failed: {e}")

def check_for_updates(text_widget=None, silent=False):
    try:
        if text_widget and not silent:
            log_message(text_widget, "Checking for updates...")

        remote_script = get_remote_script()
        if not remote_script:
            if text_widget and not silent:
                log_message(text_widget, "Could not fetch update file.")
            return False

        remote_version = extract_version_from_script(remote_script)
        if not remote_version:
            if text_widget and not silent:
                log_message(text_widget, "Could not detect remote version.")
            return False

        if parse_version(remote_version) > parse_version(APP_VERSION):
            if text_widget:
                log_message(text_widget, f"Update found: {APP_VERSION} -> {remote_version}")
            apply_update(remote_script, text_widget)
            return True
        else:
            if text_widget and not silent:
                log_message(text_widget, f"No updates found. Current version: {APP_VERSION}")
            return False

    except Exception as e:
        if text_widget and not silent:
            log_message(text_widget, f"Update check failed: {e}")
        return False

def build_debug_curl(url, headers, cookies, payload):
    parts = [f"curl {shlex.quote(url)}"]

    for key, value in headers.items():
        parts.append(f"-H {shlex.quote(f'{key}: {value}')}")

    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        parts.append(f"-b {shlex.quote(cookie_str)}")

    parts.append(f"--data-raw {shlex.quote(json.dumps(payload, separators=(',', ':')))}")

    return " \\\n  ".join(parts)

def log_message(text_widget, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    text_widget.config(state=tk.NORMAL)
    text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    text_widget.see(tk.END)
    text_widget.config(state=tk.DISABLED)

def get_latest_message(channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            messages = response.json()
            if messages:
                return messages[0]
    except Exception:
        pass
    return None

def convert_roblox_link(url):
    try:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.netloc or "").lower()
        path = parsed.path or ""
        query = urllib.parse.parse_qs(parsed.query)

        if "roblox.com" not in host:
            return None

        code = query.get("code", [None])[0]
        link_type = query.get("type", [None])[0]

        if path.lower() == "/share" and code and str(link_type).lower() == "server":
            return f"roblox://navigation/share_links?code={urllib.parse.quote(code, safe='')}&type=Server"

        place_id = query.get("placeId", [None])[0]
        link_code = query.get("privateServerLinkCode", [None])[0] or query.get("linkCode", [None])[0]

        if not place_id:
            match = re.search(r"/games/(\d+)", path)
            if match:
                place_id = match.group(1)

        if place_id and link_code:
            return f"roblox://placeId={place_id}&linkCode={urllib.parse.quote(link_code, safe='')}"

    except Exception:
        pass

    return None

def custom_http_request(referer_url, c_value, text_widget):
    api_url = "https://antisniper.manasaarohi.workers.dev/api/verify"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://antisniper.manasaarohi.workers.dev",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": referer_url,
        "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    }

    cookies = {
        "discord_session": DISCORD_SESSION
    }

    payload = {
        "token": "skipped",
        "c": c_value,
        "pageLoadTime": time.time()
    }

    debug_curl = build_debug_curl(api_url, headers, cookies, payload)

    log_message(text_widget, f"Sending verify request with c={c_value}")
    log_message(text_widget, "Debug curl command:")
    for line in debug_curl.splitlines():
        log_message(text_widget, line)

    try:
        response = requests.post(
            api_url,
            headers=headers,
            cookies=cookies,
            json=payload,
            timeout=15
        )

        log_message(text_widget, f"Verify status: {response.status_code}")
        log_message(text_widget, f"Response text: {response.text[:500]}")

        try:
            return response.json()
        except Exception:
            return {}
    except Exception as e:
        log_message(text_widget, f"HTTP Request Error: {e}")
        return {}

def poll_messages(root, text_widget):
    global last_message_ids

    for channel_id in CHANNEL_IDS:
        msg = get_latest_message(channel_id)
        if msg and msg.get("id") != last_message_ids.get(channel_id):
            last_message_ids[channel_id] = msg.get("id")

            is_recent = True
            age_seconds = 0
            timestamp_str = msg.get("timestamp")

            if timestamp_str:
                try:
                    msg_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    now_utc = datetime.now(timezone.utc)
                    age_seconds = (now_utc - msg_time).total_seconds()

                    if age_seconds > 60:
                        is_recent = False
                        log_message(
                            text_widget,
                            f"[Channel {channel_id}] Message skipped. Older than 1 minute ({int(age_seconds)}s old)."
                        )
                except Exception:
                    pass

            if is_recent:
                full_text = str(msg.get("content", ""))
                embeds = msg.get("embeds", [])

                for embed in embeds:
                    full_text += " " + str(embed.get("title", ""))
                    full_text += " " + str(embed.get("description", ""))

                    for field in embed.get("fields", []):
                        full_text += " " + str(field.get("name", ""))
                        full_text += " " + str(field.get("value", ""))

                full_text_lower = full_text.lower()

                if "ended" in full_text_lower:
                    log_message(text_widget, f"[Channel {channel_id}] Message contains 'ended'. Skipping dead link...")

                elif any(keyword in full_text_lower for keyword in KEYWORDS):
                    log_message(text_widget, f"[Channel {channel_id}] Keyword matched! Scanning for link...")

                    found_link = None

                    for embed in embeds:
                        for field in embed.get("fields", []):
                            field_name = str(field.get("name", ""))
                            field_value = str(field.get("value", ""))

                            match = re.search(r'\[.*?\]\((https?://[^\s)]+)\)', field_value)
                            if match:
                                found_link = match.group(1)
                                log_message(text_widget, f"Found link in embed field: {field_name}")
                                break

                            match = re.search(r'(https://antisniper\.manasaarohi\.workers\.dev/[^\s>]+)', field_value)
                            if match:
                                found_link = match.group(1)
                                log_message(text_widget, f"Found raw link in embed field: {field_name}")
                                break

                        if found_link:
                            break

                    if not found_link:
                        for embed in embeds:
                            description = str(embed.get("description", ""))

                            match = re.search(r'\[.*?\]\((https?://[^\s)]+)\)', description)
                            if match:
                                found_link = match.group(1)
                                log_message(text_widget, "Found link in embed description")
                                break

                            match = re.search(r'(https://antisniper\.manasaarohi\.workers\.dev/[^\s>]+)', description)
                            if match:
                                found_link = match.group(1)
                                log_message(text_widget, "Found raw link in embed description")
                                break

                    if not found_link:
                        match = re.search(r'(https://antisniper\.manasaarohi\.workers\.dev/[^\s>]+)', full_text)
                        if match:
                            found_link = match.group(1)
                            log_message(text_widget, "Found raw link in message text")

                    if found_link:
                        log_message(text_widget, f"Link found: {found_link}")
                        log_message(text_widget, f"Message age at request time: {int(age_seconds)}s")

                        if "roblox.com" in found_link:
                            roblox_link = convert_roblox_link(found_link)
                            if roblox_link:
                                log_message(text_widget, f"Converted Roblox link: {roblox_link}")
                                log_message(text_widget, "Opening Roblox protocol link...")
                                webbrowser.open(roblox_link)
                            else:
                                log_message(text_widget, "Roblox link detected, but it was not a supported private server format.")
                                webbrowser.open(found_link)

                        elif "antisniper.manasaarohi" in found_link:
                            parsed_url = urllib.parse.urlparse(found_link)
                            query_params = urllib.parse.parse_qs(parsed_url.query)
                            c_value = query_params.get("c", [None])[0]

                            if c_value:
                                data = custom_http_request(found_link, c_value, text_widget)

                                if data.get("success") and "links" in data and len(data["links"]) > 0:
                                    u_value = data["links"][0].get("u")
                                    if u_value:
                                        log_message(text_widget, f"Successfully grabbed URL: {u_value}")
                                        roblox_link = convert_roblox_link(u_value)
                                        if roblox_link:
                                            log_message(text_widget, f"Converted Roblox link: {roblox_link}")
                                            log_message(text_widget, "Opening Roblox protocol link...")
                                            webbrowser.open(roblox_link)
                                        else:
                                            log_message(text_widget, "Opening URL in web browser...")
                                            webbrowser.open(u_value)
                                    else:
                                        log_message(text_widget, "No 'u' value found in the response.")
                                else:
                                    error_text = str(data.get("error", ""))
                                    if "No decryption key matched" in error_text or "Invalid Link" in error_text:
                                        log_message(text_widget, "Link expired or decryption key no longer matches.")
                                    elif "expired" in error_text.lower():
                                        log_message(text_widget, "Link expired.")
                                    else:
                                        log_message(text_widget, f"Request failed: {error_text}")
                            else:
                                log_message(text_widget, "Could not find a 'c' value in the extracted link.")
                    else:
                        log_message(text_widget, "Keywords found, but the required link format was missing.")

    # Increased polling delay slightly to prevent Discord rate-limiting when checking multiple channels
    root.after(1000, lambda: poll_messages(root, text_widget))

def main():
    root = tk.Tk()
    root.title("Discord Link Monitor")
    root.geometry("750x450")

    log_area = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        state=tk.DISABLED,
        bg="#1e1e1e",
        fg="#00ff00",
        font=("Consolas", 10)
    )
    log_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    log_message(log_area, "Initializing UI...")
    log_message(log_area, f"App version: {APP_VERSION}")
    log_message(log_area, f"Monitoring for keywords: {', '.join(KEYWORDS)}")
    log_message(log_area, f"Monitoring {len(CHANNEL_IDS)} channel(s).")
    log_message(log_area, "Ignoring messages containing: 'ended' or older than 1 minute")
    log_message(log_area, "Listening for new messages in embeds...")

    if AUTO_UPDATE_ON_START:
        root.after(1000, lambda: check_for_updates(log_area, silent=False))

    root.after(2000, lambda: poll_messages(root, log_area))
    root.mainloop()

if __name__ == "__main__":
    main()
