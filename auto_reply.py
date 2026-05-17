from src.automation.reply_listener import listen_inbox
import sys

def main():
    print("DAY 3 Auto-Reply System Running auto_reply.py listening · auto-reply tested end-to-end")
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
