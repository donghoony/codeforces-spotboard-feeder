import datetime
import json

import handle_to_id

def make_runs_json(data, start_datetime: datetime, freeze_after):
    final_submissions = []
    with open("python_scripts/contest_info.json", "r", encoding="utf-8") as f:
        contest_data = json.load(f)
    
    def is_frozen(submission_minute):
        return submission_minute >= freeze_after

    def convert_verdict(s):
        VERDICT_CONVERT = {
            "OK" : "Yes",
            "TIME_LIMIT_EXCEEDED" : "No - Time Limit Exceeded",
            "COMPILATION_ERROR" : "No - Compilation Error",
            "RUNTIME_ERROR" : "No - Runtime Error",
            "WRONG_ANSWER" : "No - Wrong Answer",
            "MEMORY_LIMIT_EXCEEDED" : "No - Memory Limit Exceeded",
            "FAILED": "No - Failed",
            "TESTING": ""
        }
        if s not in VERDICT_CONVERT: return "No - Unexpected Running output"
        else: return VERDICT_CONVERT[s]


    for submission in data:
        # HANDLE FILTER
        if handle_to_id.handle_to_id(submission['author']['members'][0]['handle']) == 500: continue
        if "verdict" not in submission: continue
        if submission['verdict'] == "COMPILATION_ERROR": continue
        final_submissions.append(
            [   
                submission['id'],
                submission['relativeTimeSeconds'],
                submission['problem']['index'],
                submission['author']['members'][0]['handle'],
                submission['verdict'],
                submission['timeConsumedMillis'],
                submission['memoryConsumedBytes'] 
            ]
        )
    final_submissions.sort(key=lambda x: int(x[0]))
    runs = []
    final_runs = []

    for i in range(len(final_submissions)):
        submission_id, submission_time, problem_index, handle, verdict, time_elasped, memory_consumed = final_submissions[i]
        submission_time //= 60
        parsed_submission = {
            "id": submission_id,
            "team": handle_to_id.handle_to_id(handle),
            "problem": contest_data["problems"].index(problem_index),
            "result": convert_verdict(verdict),
            "frozen": is_frozen(submission_time),
            "submissionTime": submission_time,
            "timeConsumed": time_elasped,
            "memoryConsumed": memory_consumed
        }
        final_parsed_submission = {key: value for key, value in parsed_submission.items()}
        final_runs.append(final_parsed_submission)
        if is_frozen(submission_time):
            parsed_submission["result"] = ""
        runs.append(parsed_submission)

    final_json = {
        "time":{
            "contestTime": int((datetime.datetime.today() - start_datetime).total_seconds()), # TODO: Elasped Time
            "noMoreUpdate": is_frozen((datetime.datetime.today() - start_datetime).total_seconds()//60),
            "timestamp": 0
        },
        "runs": runs
    }

    final_opened_json = {
        "time":{
            "contestTime": int((datetime.datetime.today() - start_datetime).total_seconds()),
            "noMoreUpdate": True,
            "timestamp": 0
        },
        "runs": final_runs
    }
    with open("src/codeforces/runs.json", "w+") as f:
        f.write(json.dumps(final_json, indent=4))
    with open("python_scripts/final_runs.json", "w+") as f:
        f.write(json.dumps(final_opened_json, indent=4, ensure_ascii=False))
