"""
Main application for Multi-Agent Tourism System
"""
from tourism_agent import TourismAgent


def main():
    """Main application loop"""
    print("=" * 60)
    print("Welcome to the Multi-Agent Tourism System!")
    print("=" * 60)
    print("\nYou can ask about:")
    print("- Weather information for a place")
    print("- Tourist attractions in a place")
    print("- Both weather and places")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    agent = TourismAgent()
    
    while True:
        try:
            user_input = input("Enter your query: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nThank you for using the Tourism System. Goodbye!")
                break
            
            print("\n" + "-" * 60)
            response = agent.process_query(user_input)
            print(response)
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nThank you for using the Tourism System. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()

