import streamlit as st

from toolbox.utils.utils import urljoin
from toolbox.Projects.FrontEnd.utils import utils

from . import BaseTemplate


class ImageStorageTemplate(BaseTemplate):

    def __init__(self, **kwargs):
        """Create the SimplePredict Project template.
        """
        super().__init__(**kwargs)
        self.docs_url = urljoin(self.url, "docs")
        self.pagination_limit = kwargs.get("pagination_limit", 100)

    def _init_session_state(self):
        """Initialize the session state variables.
        """
        st.session_state.setdefault("error_message", None)
        st.session_state.setdefault("image_dms", None)
        st.session_state.setdefault("st_file_id", None)
        st.session_state.setdefault("upload_msg", None)
        st.session_state.setdefault("upload_success", None)
        st.session_state.setdefault("visualized_image", None)
        st.session_state.setdefault("visualized_id", None)

    def _get_image_dms(self):
        st.session_state.image_dms = list(
            self.context_cli.iterate_entities(
                entity_type="Image",
                limit=self.pagination_limit,
                order_by="!dateModified,!dateCreated,!dateObserved"
            )
        )

    def _ui_tab_images(self):
        """Define the images tab elements.
        """
        # Get the image entities
        if st.session_state.image_dms is None:
            self._get_image_dms()

        # Refresh image entities button
        col_refresh, col_search = st.columns(2, gap="small")
        with col_refresh:
            st.button("Refresh", on_click=self._get_image_dms)
        with col_search:
            id_search = st.text_input(
                "Search",
                placeholder="Search",
                label_visibility="collapsed"
            )
            id_search = utils.format_input_id(id_search)

        # Render pages
        if id_search:
            # Show a single image
            try:
                image = self.image_storage_cli.download(id_search)
                st.image(image.image, channels="BGR")
                if self.context_broker_links:
                    url = utils.get_entities_broker_link(
                        self.context_cli.broker_url,
                        image.id
                    )
                    st.markdown(
                        f"[See it in the Context Broker]({url})",
                        unsafe_allow_html=True
                    )
                st.write(self.context_cli.get_entity(
                    image.id,
                    as_dict=True
                ))
            except ValueError:
                st.warning("Image not found")
        else:
            # Show all images
            page = st.session_state.images_page \
                if "images_page" in st.session_state else 1
            if st.session_state.image_dms:
                for image in st.session_state.image_dms[page - 1]:
                    parsed_id = image.id.replace(":", "\:")
                    with st.expander(parsed_id):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(image.url, channels="BGR")
                        with col2:
                            if self.context_broker_links:
                                url = utils.get_entities_broker_link(
                                    self.context_cli.broker_url,
                                    image.id
                                )
                                st.markdown(
                                    f"[See it in the Context Broker]({url})",
                                    unsafe_allow_html=True
                                )
                            st.write(self.context_cli.get_entity(
                                image.id,
                                as_dict=True
                            ))
                # Page selector
                st.number_input(
                    "Page",
                    min_value=1,
                    max_value=max(len(st.session_state.image_dms), 1),
                    value=1,
                    key="images_page",
                )
            else:
                st.caption("No images found")

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

    def _ui_tab_visualization(self):
        """Define the visualization tab elements.
        """
        # Entity IDs input
        st.caption(
            "Double click on an empty row to add the IDs of the entities to visualize")
        entity_ids = st.experimental_data_editor(
            {"Entity IDs": [""]},
            num_rows="dynamic",
            use_container_width=True
        )
        entity_ids = [e for e in entity_ids["Entity IDs"] if e]

        # Visualizations parameters
        with st.expander("Visualization Parameters"):
            st_vis_params = st.empty()
        vis_params = utils.add_visualization_params(st_vis_params)

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
        # Title
        title_info = st.empty()
        if self.description:
            description = self.description + \
                f" The docs of the API can be found here: " +\
                f'<a href="{self.docs_url}">{self.docs_url}</a>'
            utils.write_title_info_toggle(
                self.name,
                description,
                title_info
            )
        else:
            title_info.title(self.name)

        self._st_error = st.empty()

        tab_images, tab_upload, tab_visualization = st.tabs([
            "All Images",
            "Image Upload",
            "Entity Visualization"
        ])

        with tab_images:
            self._ui_tab_images()

        with tab_upload:
            self._ui_tab_upload()

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
