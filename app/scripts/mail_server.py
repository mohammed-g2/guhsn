import time
from aiosmtpd.controller import Controller

class TestSinkHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f'\n{"="*30}')
        print(f'From: {envelope.mail_from}')
        print(f'To:   {envelope.rcpt_tos}')
        # Decoding content for readability
        content = envelope.content.decode("utf8", errors="replace")
        print(f'Message:\n{content}')
        print(f'{"="*30}\n')
        return '250 OK'

def run_server():
    handler = TestSinkHandler()
    # Explicitly using 127.0.0.1 (localhost) on port 1025
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    
    try:
        controller.start()
        print("SUCCESS: Test SMTP server is active.")
        print("Address: 127.0.0.1 | Port: 1025")
        print("Action:  Press [Ctrl + C] to stop the server.")
        
        # This is the "Windows Fix": time.sleep allows the OS to 
        # pass the KeyboardInterrupt signal to Python.
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping server via user command...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        controller.stop()
        print("Server shutdown complete.")

if __name__ == '__main__':
    run_server()