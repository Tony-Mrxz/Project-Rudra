import sys
import argparse
from llm import LLMEngine

def start_ai():
    print("==========================================")
    print("           PROJECT RUDRA - AGI            ")
    print("==========================================")
    print("[+] Initializing Rudra AI Engine...")
    
    llm = LLMEngine()
    
    print("[+] Checking LM Studio LLM Server status...")
    if not llm.ensure_server_running():
        print("[-] Could not connect to LM Studio server.")
        print("[!] Please ensure LM Studio is running and local server is turned on (port 1234).")
        return
    
    model_name = llm.get_loaded_model()
    print(f"[+] Status: Rudra is online and connected to LM Studio.")
    print(f"[+] Active Model: {model_name}")
    print("==========================================")
    print("Type 'exit' or 'quit' to end the session.\n")

    system_prompt = {
        "role": "system",
        "content": "You are Rudra, an advanced autonomous Artificial intelligence Agent Built to Help Humans with Humor. You are helpful, intelligent, precise, and direct."
    }
    
    chat_history = [system_prompt]

    while True:
        try:
            user_input = input("User > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("[+] Shutting down Rudra. Goodbye!")
                break

            chat_history.append({"role": "user", "content": user_input})
            
            print("Rudra > ", end="", flush=True)
            assistant_response = ""
            for chunk in llm.chat_stream(chat_history):
                print(chunk, end="", flush=True)
                assistant_response += chunk
            print("\n")
            
            chat_history.append({"role": "assistant", "content": assistant_response})

        except KeyboardInterrupt:
            print("\n[+] Rudra session interrupted. Goodbye!")
            break

def main():
    parser = argparse.ArgumentParser(description="Project Rudra - AGI CLI")
    parser.add_argument("command", nargs="?", default="start", help="Command to run (e.g., 'start')")

    args = parser.parse_args()

    if args.command == "start":
        start_ai()
    else:
        print(f"[-] Unknown command: '{args.command}'")
        print("Usage: rudra start")

if __name__ == "__main__":
    main()
