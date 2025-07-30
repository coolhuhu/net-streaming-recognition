function(download_asio)
  include(FetchContent)

  set(asio_URL  "https://github.com/chriskohlhoff/asio/archive/refs/tags/asio-1-34-2.tar.gz")
  set(asio_HASH "SHA256=f3bac015305fbb700545bd2959fbc52d75a1ec2e05f9c7f695801273ceb78cf5")

  # If you don't have access to the Internet,
  # please pre-download asio
  set(possible_file_locations
    ${PROJECT_SOURCE_DIR}/third-part/asio-asio-1-34-2.tar.gz
  )

  foreach(f IN LISTS possible_file_locations)
    if(EXISTS ${f})
      set(asio_URL  "${f}")
      file(TO_CMAKE_PATH "${asio_URL}" asio_URL)
      message(STATUS "Found local downloaded asio: ${asio_URL}")
      break()
    endif()
  endforeach()

  FetchContent_Declare(asio
    URL
      ${asio_URL}
    URL_HASH          ${asio_HASH}
  )

  FetchContent_GetProperties(asio)
  if(NOT asio_POPULATED)
    message(STATUS "Downloading asio ${asio_URL}")
    FetchContent_Populate(asio)
  endif()
  message(STATUS "asio is downloaded to ${asio_SOURCE_DIR}")
  # add_subdirectory(${asio_SOURCE_DIR} ${asio_BINARY_DIR} EXCLUDE_FROM_ALL)
  include_directories(${asio_SOURCE_DIR}/asio/include)
endfunction()

download_asio()