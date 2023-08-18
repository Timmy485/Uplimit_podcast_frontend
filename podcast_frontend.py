import streamlit as st
import modal
import json
import os
import wikipedia
import requests.exceptions


def main():
    st.title("Newsletter Dashboard")

    # st.image("path_to_your_image.jpg",
    #          caption="cover photo", use_column_width=True)
    
    # List of image URLs
    image_urls = [
        "cover1.jpg",
        "cover3.jpg",
        "cover2.webp",
        "cover4.webp"
    ]

    # Load custom JavaScript code
    st.markdown(
        """
        <div id="carousel" class="carousel slide" data-bs-ride="carousel">
            <div class="carousel-inner">
                <script>
                var imageUrls = """ + str(image_urls) + """;
                for (var i = 0; i < imageUrls.length; i++) {
                    var imageUrl = imageUrls[i];
                    var className = (i === 0) ? "carousel-item active" : "carousel-item";
                    document.write('<div class="' + className + '"><img src="' + imageUrl + '" class="d-block w-100" alt="..."></div>');
                }
                </script>
            </div>
            <a class="carousel-control-prev" href="#carousel" role="button" data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
            </a>
            <a class="carousel-control-next" href="#carousel" role="button" data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
            </a>
        </div>
        <style>
        .carousel-inner {
            max-height: 500px;
            overflow: hidden;
        }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.5.0/dist/js/bootstrap.bundle.min.js"></script>
        """
        , unsafe_allow_html=True
    )

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
        st.header("Newsletter Content")

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        st.image(podcast_info['podcast_details']
                 ['episode_image'], caption="Podcast Cover")
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
        # Clear the existing content
        col1.empty()
        col2.empty()
        col3.empty()
        col4.empty()

        # Call the function to process the URLs and retrieve podcast guest information
        podcast_info = process_podcast_info(url)

        # Right section - Newsletter content
        st.header("Newsletter Content")

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            st.subheader("Podcast Episode Summary")
            st.write(podcast_info['podcast_summary'])

        with col2:
            st.image(podcast_info['podcast_details']['episode_image'],
                     caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest'])

        with col4:
            try:
                podcast_guest_name = podcast_info['podcast_guest']
                try:
                    input = wikipedia.page(
                        podcast_guest_name, auto_suggest=False)
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
