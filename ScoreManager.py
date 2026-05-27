import json
import os
from datetime import date

class ScoreManager:
    MAX_HISTORY = 10

    def __init__(self, save_path="save.json"):
        self.save_path = save_path
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.save_path):
            return self._default()
        try:
            with open(self.save_path, "r") as f:
                return json.load(f)
        except Exception:
            return self._default()

    def _default(self):
        return {
            "last_name"   : "",
            "achievements": [],
            "history"     : [],
            "stats"       : {
                "total_runs"   : 0,
                "highest_score": 0,
                "highest_wave" : 0,
            }
        }

    def _save(self):
        with open(self.save_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def _recalculate_highscore(self):
        # clear all highscore flags first
        for entry in self.data["history"]:
            entry["is_highscore"] = False

        if not self.data["history"]:
            return

        # find the entry with the highest score and flag it
        best = max(self.data["history"], key=lambda e: e["score"])
        best["is_highscore"] = True

    def save_run(self, name, score, difficulty, wave_reached):
        # build the new entry
        entry = {
            "name"        : name,
            "score"       : score,
            "difficulty"  : difficulty,
            "wave_reached": wave_reached,
            "date"        : str(date.today()),
            "is_highscore": False
        }

        # insert newest first
        self.data["history"].insert(0, entry)

        # trim to max history
        self.data["history"] = self.data["history"][:self.MAX_HISTORY]

        # update last name
        self.data["last_name"] = name

        # update global stats
        self.data["stats"]["total_runs"] += 1

        if score > self.data["stats"]["highest_score"]:
            self.data["stats"]["highest_score"] = score

        if wave_reached > self.data["stats"]["highest_wave"]:
            self.data["stats"]["highest_wave"] = wave_reached

        # recalculate which entry is the highscore
        self._recalculate_highscore()

        self._save()

    def get_last_name(self):
        return self.data.get("last_name", "")

    def get_history(self):
        return self.data.get("history", [])

    def get_stats(self):
        return self.data.get("stats", {})