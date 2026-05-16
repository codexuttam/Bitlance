from src.automation.reply_listener import listen_inbox
import sys

def main():
    print("🤖 Module 3: Auto-Reply Listener Service")
    print("-" * 40)
    print("Monitoring inbox for new replies...")
    print("Press Ctrl+C to stop.")
    
    try:
        listen_inbox()
    except KeyboardInterrupt:
        print("\nListener stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
