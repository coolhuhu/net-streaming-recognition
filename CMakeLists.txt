cmake_minimum_required(VERSION 3.16)
project(net-streaming-recognizer)

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(asio)
include(portaudio)


add_executable(net-streaming-send-audio net-streaming-send-audio)
target_link_libraries(
    net-streaming-send-audio
    PUBLIC
    portaudio_static
)