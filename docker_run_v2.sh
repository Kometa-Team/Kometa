#!/bin/bash

# Install Kometa requirements
pip install -r /kometa/requirements.txt

# Define the base path
BASE_PATH="/kometa"

# Define the libraries
MOVIE_LIBRARY="Filme"
MOVIE_UHD_LIBRARY="Filme UHD"
MOVIE_SERIALS_LIBRARY="Movie Serials"
MUSIC_LIBRARY="Musik - Live"
SERIES_LIBRARY="Serien"


LIBRARIES=("$MOVIE_LIBRARY" "$MOVIE_UHD_LIBRARY" "$MOVIE_SERIALS_LIBRARY" "$MUSIC_LIBRARY" "$SERIES_LIBRARY" "")

# Function to run Kometa for all libraries
run_all() {
    python $BASE_PATH/kometa.py -r
}

# Function to update posters for a specific library
update_posters() {
    local library="$1"
    python $BASE_PATH/kometa.py -r -ov -rl "$library"
}

# Function to update collections for a specific library
update_collection() {
    local library="$1"
    python $BASE_PATH/kometa.py -r -co -rl "$library"
}

# Function to update collections for a specific library
update_metadata() {
    local library="$1"
    python $BASE_PATH/kometa.py -r -mo -rl "$library"
}

# Function to update collections for a specific library
do_operations() {
    local library="$1"
    python $BASE_PATH/kometa.py -r -op -rl "$library"
}

# Function for a complete update of a library
run_complete() {
    local library="$1"
    python $BASE_PATH/kometa.py -r -rl "$library"
}

# Select library from a list
select_library() {
    select lib in "${LIBRARIES[@]}"; do
        if [[ -n "$lib" ]]; then
            echo "$lib"
            return
        else
            echo "Invalid selection. Try again."
        fi
    done
}

# Main menu
while true; do
    clear
    echo "Kometa Docker Menu:"
    echo " 1) Run All (kometa -r)"
    echo " 2) Filme - Complete Update"
    echo " 3) Filme UHD - Complete Update"
    echo " 4) Movie Serials - Complete Update"
    echo " 5) Musik - Live - Complete Update"
    echo " 6) Serien - Complete Update"
    echo " 7) Update Posters for a Library"
    echo " 8) Update Collection for a Library"
    echo " 9) Update Metadata for a Library"
    echo "10) Do operations for a Library"
    echo "11) Exit"

    read -p "Enter your choice: " choice

    case "$choice" in
        1) run_all ;;
        2) run_complete "$MOVIE_LIBRARY" ;;
        3) run_complete "$MOVIE_UHD_LIBRARY" ;;
        4) run_complete "$MOVIE_SERIALS_LIBRARY" ;;
        5) run_complete "$MUSIC_LIBRARY" ;;
        6) run_complete "$SERIES_LIBRARY" ;;
        7)
            lib=$(select_library)
            [ -n "$lib" ] && update_posters "$lib"
            ;;
        8)
            lib=$(select_library)
            [ -n "$lib" ] && update_collection "$lib"
            ;;
        9)
            lib=$(select_library)
            [ -n "$lib" ] && update_metadata "$lib"
            ;;
        10)
            lib=$(select_library)
            [ -n "$lib" ] && do_operations "$lib"
            ;;
        11) exit ;;
        *) echo "Invalid option. Try again." ;;
    esac

    read -p "Press Enter to continue..."
done
