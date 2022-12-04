import json

def make_constest_json():
    with open("python_scripts/contest_info.json", "r", encoding="utf-8") as f:
        contest_data = json.load(f)
    
    balloons = contest_data["balloon_colors"]
    problems = [
        {
            "id": idx, 
            "name": problem_name,
            "color": balloons[idx],
            "title": problem_name    
        } for idx, problem_name in enumerate(contest_data["problems"], start=0)
        ]
    handles = [
        {
            "id": idx,
            "name" : handle
        } for idx, handle in enumerate(contest_data["contestants"], start=1)
    ]
    h2i = {
        i["name"].lower(): i["id"] for i in handles
    }

    h2i = {}
    handles = []
    contestants_data = contest_data["contestants"]
    for i in range(1, len(contestants_data)+1):
        handle, name, major = contestants_data[i-1].split()
        h2i[handle.lower()] = i
        handles.append({
            "id": i,
            "name" : f"{name} ({major})"
        })

    final_contest_data = {
        "title" : contest_data["title"],
        "systemName": "Codeforces, Konkuk University",
        "systemVersion" : "",
        "problems" : problems,
        "teams": handles
    }
    with open("src/codeforces/contest.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(final_contest_data, indent=4, ensure_ascii=False))
    with open("python_scripts/handle_to_id.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(h2i, indent=4, ensure_ascii=False))

make_constest_json()