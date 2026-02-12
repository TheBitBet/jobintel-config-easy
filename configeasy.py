# scripts/config_wizard.py
import ruamel.yaml
from pathlib import Path

CONFIG_PATH = Path("config/default.yml")

yaml = ruamel.yaml.YAML()

def load_config():
    with CONFIG_PATH.open() as f:
        return yaml.load(f)

def save_config(cfg):
    with CONFIG_PATH.open("w") as f:
        yaml.dump(cfg, f)

def ask_list(prompt, current):
    print(f"{prompt} (comma-separated). Current: {', '.join(current) or '(none)'}")
    raw = input("> ").strip()
    if not raw:
        return current
    return [item.strip() for item in raw.split(",") if item.strip()]

def main():
    cfg = load_config()

    roles = cfg["scoring"]["include"]["roles"]
    roles = ask_list("Roles to include", roles)
    cfg["scoring"]["include"]["roles"] = roles

    skills = cfg["scoring"]["include"]["skills"]
    skills = ask_list("Skills to include", skills)
    cfg["scoring"]["include"]["skills"] = skills

    exclude_kw = cfg["scoring"]["exclude"]["keywords"]
    exclude_kw = ask_list("Keywords to exclude", exclude_kw)
    cfg["scoring"]["exclude"]["keywords"] = exclude_kw

    boards = cfg["sources"]["greenhouse"]["boards"]
    boards = ask_list("Greenhouse boards", boards)
    cfg["sources"]["greenhouse"]["boards"] = boards

    save_config(cfg)
    print("Config updated.")

if __name__ == "__main__":
    main()
