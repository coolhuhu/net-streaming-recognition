import socket
import threading
import wave
import time

class SpeechRecognitionServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.audio_buffer = bytearray()
        
    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Speech recognition server started, listening on {self.host}:{self.port}")
        
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Client connected from: {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()
            
    def handle_client(self, client_socket):
        # Buffer to store audio data for this client
        client_audio_buffer = bytearray()
        
        try:
            while True:
                # Receive audio data from client
                data = client_socket.recv(4096)
                if not data:
                    # Client disconnected
                    break
                    
                # Add received data to buffer
                client_audio_buffer.extend(data)
                
                # Simulate speech recognition processing
                # In a real implementation, you would process the audio data here
                recognition_result = self.simulate_recognition(data)
                
                # Send recognition result back to client
                if recognition_result:
                    try:
                        client_socket.send(recognition_result.encode('utf-8'))
                    except:
                        # Client may have disconnected
                        break
                        
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Client disconnected, save audio data to file
            if len(client_audio_buffer) > 0:
                self.save_audio_to_wav(client_audio_buffer, f"recorded_audio_{int(time.time())}.wav")
                print(f"Audio saved to file, total bytes: {len(client_audio_buffer)}")
            client_socket.close()
            
    def simulate_recognition(self, audio_data):
        # This is a simulated recognition function
        # In a real implementation, you would replace this with actual speech recognition code
        # For demonstration, we'll return some text every few chunks
        
        # Simple simulation: return text occasionally
        import random
        if random.random() < 0.3:  # 30% chance to return result
            simulated_results = [
                "Hello ",
                "world ",
                "this ",
                "is ",
                "a ",
                "test ",
                "of ",
                "real-time ",
                "speech ",
                "recognition.\n"
            ]
            return random.choice(simulated_results)
        return ""
        
    def save_audio_to_wav(self, audio_data, filename):
        # Save the received audio data as a WAV file
        try:
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)   # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_data)
            print(f"Audio saved to {filename}")
        except Exception as e:
            print(f"Error saving audio to file: {e}")

def main():
    import sys
    
    host = 'localhost'
    port = 8080
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
        
    server = SpeechRecognitionServer(host, port)
    server.start_server()

if __name__ == "__main__":
    main()