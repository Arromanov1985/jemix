import subprocess
from pathlib import Path
import sys

ROOT = Path("voice/modules")

def main():
    lessons = []
    for p in sorted(ROOT.glob("module-*/lesson-*")):
        if list(p.glob("slide*.ssml")):
            lessons.append(p)

    if not lessons:
        print("No voice lessons found")
        return 1

    print(f"Lessons found: {len(lessons)}")

    for lesson in lessons:
        print(f"\n=== {lesson} ===")
        result = subprocess.run(
            [sys.executable, "scripts/salute_tts_v2.py", str(lesson)],
            text=True
        )
        if result.returncode != 0:
            print(f"FAILED: {lesson}")
            return result.returncode

    print("\nAll voice audio generated.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
