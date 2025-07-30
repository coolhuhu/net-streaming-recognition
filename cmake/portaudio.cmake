function(download_portaudio)
  include(FetchContent)

  set(portaudio_URL  "https://github.com/PortAudio/portaudio/archive/refs/tags/v19.7.0.zip")
  set(portaudio_HASH "SHA256=ce1e7b27ad362cb9745de7da3d266a996b085ca75a12ac62c881f88ab6894acf")

  # If you don't have access to the Internet, please download it to your
  # local drive and modify the following line according to your needs.
  set(possible_file_locations
    $ENV{HOME}/Downloads/pa_stable_v190700_20210406.tgz
    $ENV{HOME}/asr/pa_stable_v190700_20210406.tgz
    ${CMAKE_SOURCE_DIR}/pa_stable_v190700_20210406.tgz
    ${CMAKE_BINARY_DIR}/pa_stable_v190700_20210406.tgz
    /tmp/pa_stable_v190700_20210406.tgz
    /star-fj/fangjun/download/github/pa_stable_v190700_20210406.tgz
  )

  foreach(f IN LISTS possible_file_locations)
    if(EXISTS ${f})
      set(portaudio_URL  "${f}")
      file(TO_CMAKE_PATH "${portaudio_URL}" portaudio_URL)
      message(STATUS "Found local downloaded portaudio: ${portaudio_URL}")
      break()
    endif()
  endforeach()

  # Always use static build
  set(PA_BUILD_SHARED OFF CACHE BOOL "" FORCE)
  set(PA_BUILD_STATIC ON CACHE BOOL "" FORCE)

  FetchContent_Declare(portaudio
    URL
      ${portaudio_URL}
    URL_HASH          ${portaudio_HASH}
  )

  FetchContent_GetProperties(portaudio)
  if(NOT portaudio_POPULATED)
    message(STATUS "Downloading portaudio from ${portaudio_URL}")
    FetchContent_Populate(portaudio)
  endif()
  message(STATUS "portaudio is downloaded to ${portaudio_SOURCE_DIR}")
  message(STATUS "portaudio's binary dir is ${portaudio_BINARY_DIR}")

  if(APPLE)
    set(CMAKE_MACOSX_RPATH ON) # to solve the following warning on macOS
  endif()

  add_subdirectory(${portaudio_SOURCE_DIR} ${portaudio_BINARY_DIR} EXCLUDE_FROM_ALL)

  set_target_properties(portaudio_static PROPERTIES OUTPUT_NAME "sherpa-onnx-portaudio_static")
  if(NOT WIN32)
    target_compile_options(portaudio_static PRIVATE "-Wno-deprecated-declarations")
  endif()

  if(NOT BUILD_SHARED_LIBS AND SHERPA_ONNX_ENABLE_BINARY)
    install(TARGETS
      portaudio_static
    DESTINATION lib)
  endif()

endfunction()

download_portaudio()

# Note
# See http://portaudio.com/docs/v19-doxydocs/tutorial_start.html
# for how to use portaudio
