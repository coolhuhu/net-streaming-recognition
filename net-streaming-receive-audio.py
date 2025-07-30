#!/usr/bin/env python3

import socket
import wave
import sys
import struct

def save_wav_file(filename, audio_data):
    """
    Save audio data to a WAV file with 16k sample rate, 16-bit, mono format.
    """
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit (2 bytes)
        wav_file.setframerate(16000)  # 16kHz sample rate
        wav_file.writeframes(audio_data)
    print(f"Audio saved to {filename}")

def run_server(host, port):
    """
    Run the TCP server to receive audio data and save it to a WAV file.
    """
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}")
        
        while True:
            print("Waiting for client connection...")
            client_socket, client_address = server_socket.accept()
            print(f"Client connected from {client_address}")
            
            # Buffer to store all audio data
            audio_buffer = bytearray()
            
            try:
                while True:
                    # Receive data from client
                    data = client_socket.recv(4096)
                    if not data:
                        # Client disconnected
                        break
                    
                    # Add received data to buffer
                    audio_buffer.extend(data)
                    
            except ConnectionResetError:
                print("Client connection reset")
            except Exception as e:
                print(f"Error receiving data: {e}")
            finally:
                # Client disconnected, save audio to file
                client_socket.close()
                if audio_buffer:
                    filename = "received_audio.wav"
                    save_wav_file(filename, audio_buffer)
                    print(f"Received {len(audio_buffer)} bytes of audio data")
                else:
                    print("No audio data received")
            
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: {} <host> <port>".format(sys.argv[0]))
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    run_server(host, port)

if __name__ == "__main__":
    main()