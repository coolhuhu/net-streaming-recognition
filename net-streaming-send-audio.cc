#include <asio.hpp>
#include <chrono>
#include <csignal>
#include <cstring>
#include <iostream>
#include <portaudio.h>
#include <vector>

class AudioStreamClient {
private:
  // Audio parameters
  static constexpr int SAMPLE_RATE = 16000;
  static constexpr int FRAMES_PER_BUFFER = 1024;
  static constexpr int BYTES_PER_SAMPLE = 2; // 16-bit audio

  // Network parameters
  std::string server_ip_;
  std::string server_port_;

  // ASIO context and socket
  asio::io_context io_context_;
  asio::ip::tcp::socket socket_;

  // PortAudio stream
  PaStream *pa_stream_;

  // Buffer for audio data
  std::vector<char> audio_buffer_;
  size_t buffer_size_ms_;

  // Flag to control streaming
  std::atomic<bool> is_streaming_;

public:
  AudioStreamClient(const std::string &ip, const std::string &port,
                    size_t buffer_ms = 200)
      : server_ip_(ip), server_port_(port), socket_(io_context_),
        buffer_size_ms_(buffer_ms), is_streaming_(false) {
    audio_buffer_.resize(SAMPLE_RATE * BYTES_PER_SAMPLE * buffer_ms / 1000);
  }

  ~AudioStreamClient() { stop(); }

  bool initialize() {
    // Initialize PortAudio
    PaError err = Pa_Initialize();
    if (err != paNoError) {
      std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
      return false;
    }

    // Open PortAudio stream
    PaStreamParameters inputParameters;
    inputParameters.device = Pa_GetDefaultInputDevice();
    if (inputParameters.device == paNoDevice) {
      std::cerr << "Error: No default input device." << std::endl;
      return false;
    }

    inputParameters.channelCount = 1;       // mono
    inputParameters.sampleFormat = paInt16; // 16-bit
    inputParameters.suggestedLatency =
        Pa_GetDeviceInfo(inputParameters.device)->defaultLowInputLatency;
    inputParameters.hostApiSpecificStreamInfo = nullptr;

    err = Pa_OpenStream(&pa_stream_, &inputParameters, nullptr, SAMPLE_RATE,
                        FRAMES_PER_BUFFER, paClipOff, nullptr, nullptr);
    if (err != paNoError) {
      std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
      return false;
    }

    return true;
  }

  bool connect() {
    try {
      asio::ip::tcp::resolver resolver(io_context_);
      auto endpoints = resolver.resolve(server_ip_, server_port_);
      asio::connect(socket_, endpoints);
      std::cout << "Connected to server " << server_ip_ << ":" << server_port_
                << std::endl;
      return true;
    } catch (std::exception &e) {
      std::cerr << "Connection error: " << e.what() << std::endl;
      return false;
    }
  }

  void startStreaming() {
    if (!pa_stream_) {
      std::cerr << "PortAudio stream not initialized" << std::endl;
      return;
    }

    PaError err = Pa_StartStream(pa_stream_);
    if (err != paNoError) {
      std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
      return;
    }

    is_streaming_ = true;

    // Start audio capture and send loop
    sendAudioData();
  }

  void stop() {
    is_streaming_ = false;

    // Send any remaining data before closing
    if (!audio_buffer_.empty()) {
      try {
        asio::write(socket_, asio::buffer(audio_buffer_));
      } catch (std::exception &e) {
        std::cerr << "Error sending remaining data: " << e.what() << std::endl;
      }
    }

    if (pa_stream_) {
      Pa_CloseStream(pa_stream_);
      pa_stream_ = nullptr;
    }

    if (socket_.is_open()) {
      socket_.close();
    }

    Pa_Terminate();
  }

private:
  void sendAudioData() {
    const size_t buffer_size_bytes = audio_buffer_.size();
    const size_t frames_per_buffer = buffer_size_bytes / BYTES_PER_SAMPLE;

    while (is_streaming_) {
      // Read audio data from microphone
      PaError err =
          Pa_ReadStream(pa_stream_, audio_buffer_.data(), frames_per_buffer);
      if (err) {
        std::cerr << "PortAudio error: " << Pa_GetErrorText(err) << std::endl;
        break;
      }

      // Send audio data to server
      try {
        asio::write(socket_, asio::buffer(audio_buffer_, buffer_size_bytes));
      } catch (std::exception &e) {
        std::cerr << "Network send error: " << e.what() << std::endl;
        break;
      }
    }
  }
};

// Global pointer to client for signal handler
AudioStreamClient *g_client = nullptr;

void signalHandler(int signal) {
  std::cout << "\nReceived signal " << signal << ", shutting down..."
            << std::endl;
  if (g_client) {
    g_client->stop();
  }
  exit(0);
}

int main(int argc, char *argv[]) {
  if (argc != 3 && argc != 4) {
    std::cerr << "Usage: " << argv[0]
              << " <server_ip> <server_port> [buffer_ms]" << std::endl;
    return 1;
  }

  std::string server_ip = argv[1];
  std::string server_port = argv[2];
  size_t buffer_ms = (argc == 4) ? std::stoi(argv[3]) : 200; // default 200ms

  AudioStreamClient client(server_ip, server_port, buffer_ms);

  // Set global pointer for signal handler
  g_client = &client;

  // Register signal handler for Ctrl+C
  std::signal(SIGINT, signalHandler);

  if (!client.initialize()) {
    std::cerr << "Failed to initialize client" << std::endl;
    return 1;
  }

  if (!client.connect()) {
    std::cerr << "Failed to connect to server" << std::endl;
    return 1;
  }

  std::cout << "Starting audio streaming with " << buffer_ms << "ms buffer..."
            << std::endl;
  std::cout << "Press Ctrl+C to stop" << std::endl;

  client.startStreaming();

  return 0;
}