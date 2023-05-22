import streamlit as st
import pandas as pd

from toolbox.Context import entity_parser
from toolbox.Visualization.Defaults import Defaults

from . import BaseTemplate


class ImageStorageTemplate(BaseTemplate):

    def __init__(self, **kwargs):
        """Create the SimplePredict Project template.
        """
        super().__init__(**kwargs)
        self.pagination_limit = kwargs.get("pagination_limit", 100)

        vis_defaults = Defaults.dict()
        self._vis_params_values = [str(v) for v in vis_defaults.values()]
        self._vis_params_keys = list(vis_defaults.keys())

        # Streamlit elements

    def _init_session_state(self):
        """Initialize the session state variables.
        """
        if "error_message" not in st.session_state:
            st.session_state.error_message = None
        if "image_dms" not in st.session_state:
            st.session_state.image_dms = None
        if "st_file_id" not in st.session_state:
            st.session_state.st_file_id = None
        if "upload_msg" not in st.session_state:
            st.session_state.upload_msg = None
        if "upload_success" not in st.session_state:
            st.session_state.upload_success = None
        if "visualized_image" not in st.session_state:
            st.session_state.visualized_image = None
        if "visualized_id" not in st.session_state:
            st.session_state.visualized_id = None

    def _get_image_dms(self):
        st.session_state.image_dms = list(
            self.context_cli.iterate_entities(
                entity_type="Image",
                limit=self.pagination_limit
            )
        )

    def _ui_tab_images(self):
        """Define the images tab elements.
        """
        # Get the image entities
        if st.session_state.image_dms is None:
            self._get_image_dms()

        # Refresh image entities button
        st.button("Refresh", on_click=self._get_image_dms)

        # Render pages
        page = st.session_state.images_page \
            if "images_page" in st.session_state else 1
        for image in st.session_state.image_dms[page - 1]:
            parsed_id = image.id.replace(":", "\:")
            with st.expander(parsed_id):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(image.url, channels="BGR")
                with col2:
                    st.write(entity_parser.data_model_to_json(image))

        # Page selector
        st.number_input(
            "Page",
            min_value=1,
            max_value=max(len(st.session_state.image_dms), 1),
            value=1,
            key="images_page",
        )

    def _upload_image(self):
        """Uploads an image to the image storage.
        """
        uploaded_file = st.session_state.uploaded_file
        if st.session_state.st_file_id != uploaded_file.id:
            try:
                image_id = self.image_storage_cli.upload_bytes(
                    image_bytes=uploaded_file.read(),
                    name=uploaded_file.name,
                    file_type=uploaded_file.type,
                    source=st.session_state.upload_source,
                    purpose=st.session_state.upload_purpose
                )
                st.session_state.st_file_id = uploaded_file.id
                st.session_state.upload_msg = ("Uploaded image with ID: "
                                               + image_id.replace(':', '\:'))
                st.session_state.upload_success = True
            except Exception as e:
                self.logger.exception(e, exc_info=True)
                st.session_state.upload_msg = f"Error uploading image: {e}"
                st.session_state.upload_success = False
        else:
            st.session_state.upload_msg = "File already uploaded"
            st.session_state.upload_success = False

    def _visualize_entities(self, entity_ids, vis_params):
        """Visualize the entities in a single image.
        """
        st.session_state.visualized_image = None
        if not entity_ids:
            return
        try:
            vis_id = self.image_storage_cli.visualize(
                entity_ids,
                visualization_params=vis_params
            )
            st.session_state.visualized_id = vis_id
            image = self.image_storage_cli.download(vis_id)
            st.session_state.visualized_image = image
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"

    def _ui_tab_upload(self):
        """Define the upload tab elements.
        """

        st.file_uploader(
            "Upload Image",
            type=["png", "jpg", "jpeg", "bmp", "tiff"],
            key="uploaded_file",
        )
        st.text_input(
            "source",
            key="upload_source",
            placeholder="e.g. urn:ngsi-ld:Camera:C1"
        )
        st.text_input(
            "purpose",
            key="upload_purpose",
            placeholder="e.g. InstanceSegmentation"
        )
        st.button(
            "Upload",
            on_click=self._upload_image,
            use_container_width=True,
            disabled=st.session_state.uploaded_file is None
        )

        # Clear the upload message if no file is selected
        if st.session_state.uploaded_file is None:
            st.session_state.upload_msg = None

        # Show the upload message
        if st.session_state.upload_msg is not None:
            if st.session_state.upload_success:
                st.success(st.session_state.upload_msg)
            else:
                st.error(st.session_state.upload_msg)

    def _ui_tab_download(self):
        """Define the download tab elements.
        """
        image_id = st.text_input(
            "Image ID",
            placeholder="e.g. urn:ngsi-ld:Image:IMG1"
        )

        if image_id:
            try:
                image = self.image_storage_cli.download(image_id)
                st.image(image.image, channels="BGR")
            except Exception as e:
                self.logger.exception(e, exc_info=True)
                st.error(f"Error downloading image: {e}")

    def _ui_tab_visualization(self):
        """Define the visualization tab elements.
        """
        # Entity IDs input
        st.caption("Double click on an empty row to add the IDs of the entities to visualize")
        entity_ids = st.experimental_data_editor(
            {"Entity IDs": [""]},
            num_rows="dynamic",
            use_container_width=True
        )
        entity_ids = [e for e in entity_ids["Entity IDs"] if e]

        # Visualizations parameters
        vis_params = {}
        with st.expander("Visualization Parameters"):
            vis_params = st.experimental_data_editor(
                {
                    "Parameters": self._vis_params_keys,
                    "Values": self._vis_params_values,
                },
                use_container_width=True,
            )
            vis_params = dict(zip(vis_params["Parameters"],
                                    vis_params["Values"]))
        
        # Visualize button
        st.button(
            "Visualize",
            on_click=self._visualize_entities,
            args=(entity_ids, vis_params),
            use_container_width=True
        )

        # Show image
        if st.session_state.visualized_image is not None:
            st.image(st.session_state.visualized_image.image, channels="BGR")
            st.caption(
                "Image ID: "
                + st.session_state.visualized_id.replace(':', '\:')
            )

    def _ui(self):
        """Set the UI elements.
        """
        st.title(self.name)
        self._st_error = st.empty()

        tab_images, tab_upload, tab_download, tab_visualization = st.tabs([
            "All Images",
            "Image Upload",
            "Image Retrieval",
            "Entity Visualization"
        ])

        with tab_images:
            self._ui_tab_images()

        with tab_upload:
            self._ui_tab_upload()

        with tab_download:
            self._ui_tab_download()

        with tab_visualization:
            self._ui_tab_visualization()

    def _update(self):
        """Handle the UI logic.
        """
        # Show the error message if any
        if st.session_state.error_message is not None:
            self._st_error.error(st.session_state.error_message)
        else:
            self._st_error.empty()
        st.session_state.error_message = None

    def __call__(self):
        self._init_session_state()
        self._ui()
        self._update()
