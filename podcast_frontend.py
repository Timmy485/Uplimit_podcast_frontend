import streamlit as st
import modal
import json
import os
import wikipedia
import requests.exceptions


def main():
    st.image("cover6.png",
             use_column_width=True)
    st.markdown("<h1 style='text-align: center;'>PODCAST DISCOVERY NEWSLETTER GENERATOR</h1>", unsafe_allow_html=True)
    # st.title("PODCAST DISCOVERY NEWSLETTER GENERATOR")

    available_podcast_info = create_dict_from_json_files('.')

    # Left section - Input fields
    st.sidebar.header("Podcast RSS Feeds")

    # Dropdown box
    st.sidebar.subheader("Available Podcasts Feeds")
    selected_podcast = st.sidebar.selectbox(
        "Select Podcast", options=available_podcast_info.keys())

    if selected_podcast:

        podcast_info = available_podcast_info[selected_podcast]

        # Right section - Newsletter content
        st.subheader("Podcast Name")
        st.write(podcast_info['podcast_details']['podcast_title'])
        st.image(podcast_info['podcast_details']
                 ['episode_image'])

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        st.subheader("Podcast Episode Summary")
        st.write(podcast_info['podcast_summary'])

        st.subheader("Podcast Guest")
        st.write(podcast_info['podcast_guest'])
        try:
            podcast_guest_name = podcast_info['podcast_guest']
            try:
                input = wikipedia.page(podcast_guest_name, auto_suggest=False)
                podcast_guest_info = input.summary
                st.write(podcast_guest_info)
            except wikipedia.exceptions.DisambiguationError as e:
                st.write(
                    f"Multiple possible meanings for {podcast_guest_name}. Details unavailable for now")
            except wikipedia.exceptions.PageError:
                st.write("No Info found")
        except KeyError:
            st.write("Guest name not available")

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)

    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed")

    process_button = st.sidebar.button("Process Podcast Feed")
    st.sidebar.markdown(
        "**Note**: Podcast processing can take upto 5 mins, please be patient.")

    if process_button:
        # Call the function to process the URLs and retrieve podcast guest information
        podcast_info = process_podcast_info(url)

        # Right section - Newsletter content
        st.header("Podcast Name")
        st.write(podcast_info['podcast_details']['podcast_title'])

        st.image(podcast_info['podcast_details']
                 ['episode_image'])

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        st.subheader("Podcast Episode Summary")
        st.write(podcast_info['podcast_summary'])

        st.subheader("Podcast Guest")
        st.write(podcast_info['podcast_guest'])
        try:
            podcast_guest_name = podcast_info['podcast_guest']
            try:
                input = wikipedia.page(podcast_guest_name, auto_suggest=False)
                podcast_guest_info = input.summary
                st.write(podcast_guest_info)
            except wikipedia.exceptions.DisambiguationError as e:
                st.write(
                    f"Multiple possible meanings for {podcast_guest_name}. Details unavailable for now")
            except wikipedia.exceptions.PageError:
                st.write("No Info found")
        except KeyError:
            st.write("Guest name not available")

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)


def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict


def process_podcast_info(url):
    try:
        f = modal.Function.lookup("corise-podcast-project", "process_podcast")
        output = f.call(url, '/content/podcast/')
        return output
    except requests.exceptions.ConnectTimeout:
        return {"error": "Connection timeout. Please check the podcast URL and your internet connection."}


if __name__ == '__main__':
    main()
