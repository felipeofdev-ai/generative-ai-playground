from offline_eval import run_offline_eval

def run() -> dict:
    return {"benchmark": "nexusai-core", **run_offline_eval()}

if __name__ == "__main__":
    print(run())
