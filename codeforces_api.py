from datetime import datetime, timedelta
import hashlib
import random
import requests
import time
import json

import codeforces_parser
import codeforces_contests

from secret import KEY, SECRET # API Secret key at secret.py

def codeforce_auth_request(contest_id, api, verbose=False):
    CONTEST_ID = contest_id

    RAND = random.randint(100_000, 999_999)
    TIME = str(int(time.time()))

    params = sorted([
        ("contestId", CONTEST_ID),
        ("apiKey", KEY),
        ("time", TIME)
    ])

    s = f"{RAND}/{api}?"
    for p, q in params:
        s += (p + "=" + q + "&")

    APISIG = s[:-1] + f"#{SECRET}"
    DIGESTED_APISIG = hashlib.sha512(APISIG.encode("utf-8")).hexdigest()
    URL = f"https://codeforces.com/api/{api}?contestId={CONTEST_ID}&apiKey={KEY}&time={TIME}&apiSig={RAND}{DIGESTED_APISIG}"
    if verbose:
        print(f"URL : {URL}")
    res = requests.get(URL)
    if res.status_code != 200:
        print(f"Invalid Status Code: {res.status_code}")
        raise ValueError
    data = res.json()
    if data['status'] != "OK":
        print(f"Invalid Status Code: {data['status']}")
        exit(1)
    return data

def get_contest_data(contest_id, verbose):
    # TODO: get only new data, not entire data (too big)
    return codeforce_auth_request(contest_id, "contest.standings", verbose)

def get_contest_submissions(contest_id, verbose):
    return codeforce_auth_request(contest_id, "contest.status", verbose)

def wait_contest_until_start(cid, verbose):
    while 1:
        try:
            contest_data = get_contest_data(cid, verbose)["result"]["contest"]
            break
        except:
            # TODO: sleep until contest start time, specify except error
            print("Contest has not started, waiting...") 
            time.sleep(30)
    return contest_data


if __name__ == "__main__":
    with open("python_scripts/contest_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        CONTEST_ID, FREEZE_AFTER, VERBOSE = data["contest_id"], data["freeze_after"], data["verbose"]

    contest_data = wait_contest_until_start(CONTEST_ID, VERBOSE)
    CONTEST_START_DATE = datetime.fromtimestamp(contest_data["startTimeSeconds"])
    CONTEST_DURATION = contest_data["durationSeconds"]

    is_contest_running = lambda: CONTEST_START_DATE + timedelta(seconds=CONTEST_DURATION) >= datetime.now()

    while 1:
        t = datetime.now()

        # Update Contest Details, Contestant list
        codeforces_contests.make_constest_json()
        print(f"{t.hour:02d}:{t.minute:02d}:{t.second:02d} Updated Contest", end="...")

        try:
            data = get_contest_submissions(CONTEST_ID, VERBOSE)
        except:
            continue

        runs_json = codeforces_parser.make_runs_json(data['result'], start_datetime=CONTEST_START_DATE, freeze_after=FREEZE_AFTER)
        print("Fetch OK", end="...\n")

        if not is_contest_running():
            break

        time.sleep(5)

    print("-- Contest is over --")