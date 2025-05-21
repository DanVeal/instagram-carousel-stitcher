
import streamlit as st
import instaloader
from PIL import Image
import os
import re
import tempfile

def download_carousel_images(post_url, output_dir):
    shortcode = re.search(r"/p/([^/]+)/", post_url)
    if not shortcode:
        st.error("Invalid Instagram post URL.")
        return []

    shortcode = shortcode.group(1)
    loader = instaloader.Instaloader(download_videos=False, download_comments=False, save_metadata=False)

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
    except Exception as e:
        st.error(f"Error fetching post: {e}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    for i, node in enumerate(post.get_sidecar_nodes(), start=1):
        image_url = node.display_url
        image_data = loader.context.get_raw(image_url)
        img_path = os.path.join(output_dir, f"{shortcode}_{i}.jpg")
        with open(img_path, "wb") as f:
            f.write(image_data)
        image_paths.append(img_path)

    return image_paths

def stitch_images(image_paths, output_file):
    images = [Image.open(path) for path in image_paths]
    widths, heights = zip(*(img.size for img in images))
    total_width = sum(widths)
    max_height = max(heights)

    stitched_image = Image.new("RGB", (total_width, max_height), (255, 255, 255))

    x_offset = 0
    for img in images:
        stitched_image.paste(img, (x_offset, 0))
        x_offset += img.width

    stitched_image.save(output_file)
    return output_file

st.title("📸 Instagram Carousel Stitcher")
post_url = st.text_input("Enter Instagram Carousel Post URL:")

if st.button("Download and Stitch"):
    if not post_url:
        st.warning("Please enter a valid Instagram post URL.")
    else:
        with st.spinner("Processing..."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                image_paths = download_carousel_images(post_url, tmp_dir)
                if image_paths:
                    output_file = os.path.join(tmp_dir, "stitched_carousel.jpg")
                    stitched_image_path = stitch_images(image_paths, output_file)
                    st.success("Stitched image created successfully!")
                    st.image(stitched_image_path, caption="Stitched Carousel", use_column_width=True)
                    with open(stitched_image_path, "rb") as file:
                        btn = st.download_button(
                            label="Download Stitched Image",
                            data=file,
                            file_name="stitched_carousel.jpg",
                            mime="image/jpeg"
                        )
                else:
                    st.error("Failed to download images from the provided URL.")
