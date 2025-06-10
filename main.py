from app_controller import AppController
import traceback

if __name__ == "__main__":
    try:
        controller = AppController()
        controller.start()
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")