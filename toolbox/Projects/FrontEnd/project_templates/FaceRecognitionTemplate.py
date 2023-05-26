from typing import List, Optional, Union

import requests
import streamlit as st

from toolbox.Projects.FrontEnd.utils import utils
from toolbox.Structures import Image
from toolbox.utils.utils import urljoin


from . import SimplePredictTemplate


class FaceRecognitionTemplate(SimplePredictTemplate):

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

        # Error message
        self._st_error = st.empty()

        # Input and output columns
        col_input, col_output = st.columns(2, gap="large")

        # Input column
        with col_input:
            st.subheader("Input")
            st.text_input(
                "Input ID",
                placeholder="e.g. urn:ngsi-ld:Image:IMG1",
                key="input_id",
                disabled=(
                    "uploaded_file" in st.session_state and
                    st.session_state.uploaded_file is not None
                )
            )
            st.write(
                "<p style='color: gray; text-align: center;'>- or -</p>",
                unsafe_allow_html=True
            )
            st.file_uploader(
                "Upload an image",
                type=self._upload_mimes,
                key="uploaded_file",
            )
            with st.expander("Advanced"):
                st.radio(
                    "Accept",
                    options=["application/json", "application/ld+json"],
                    key="accept_header",
                )
                st.markdown("Visualization parameters")
                st_vis_params = st.empty()
            st.session_state.visualization_parameters = \
                utils.add_visualization_params(st_vis_params)

            self._st_button_predict = st.empty()
            self._st_button_extract = st.empty()
            self._st_button_recognize = st.empty()
            st.divider()
            self._st_input_image = st.empty()
            self._st_preview_image_id = st.empty()

        with col_output:
            st.subheader("Output")
            self._st_output_image = st.empty()
            st.divider()
            self._st_output_text = st.empty()
            self._st_output_json = st.empty()
    
    def _init_session_state(self):
        super()._init_session_state()
        st.session_state.setdefault("input_entity", None)

    def _set_input_entity_by_id(self, entity_id: str) -> bool:
        st.session_state.input_entity = self.context_cli.get_entity(
            entity_id,
            as_dict=True
        )

    def _get_image_from_input(self):
        """Get the input image from  the input entity.
        """
        entity = st.session_state.input_entity
        image_id = None
        
        # No input entity
        if entity is None:
            st.session_state.input_image = None
            return

        # Get the image ID
        if entity["type"] == "Image":
            image_id = entity["id"]
        elif "image" in entity:
            if "object" in entity["image"]:
                image_id = entity["image"]["object"]
            elif "value" in entity["image"]:
                image_id = entity["image"]["value"]
        
        # No image on entity
        if not image_id:
            st.session_state.input_image = None
            return

        # Image already set
        if st.session_state.input_image is not None and \
            st.session_state.input_image.id == image_id:
            return
        
        # Download the image
        try:
            image = self.image_storage_cli.download(image_id)
            st.session_state.input_image = image
        except:
            st.session_state.error_message = "Error: Image " + \
                utils.format_id(image_id) + \
                f" not found on {self.image_storage_cli.url}"
            return False
    
    def _show_input_image(self):
        """Show the input image or entity and id caption.
        """
        if st.session_state.input_image is not None:
            self._st_input_image.image(
                st.session_state.input_image.image,
                channels="BGR"
            )
            self._st_preview_image_id.caption(
                utils.format_id(st.session_state.input_image.id)
            )
        elif st.session_state.input_entity is not None:
            self._st_input_image.write(st.session_state.input_entity)
            self._st_preview_image_id.caption(
                utils.format_id(st.session_state.input_image.id)
            )
        else:
            self._st_input_image.empty()
            self._st_preview_image_id.empty()

    def _show_output(self):
        """Show the output image and JSON.
        """
        # Show the output image if any
        if st.session_state.output_image is not None:
            self._st_output_image.image(
                st.session_state.output_image.image,
                channels="BGR"
            )
        else:
            self._st_output_image.empty()

        # Show the output JSON if any
        if st.session_state.output_json is not None:
            if len(st.session_state.output_json) == 0:
                self._st_output_image.warning("No entities found")
            else:
                if self.context_broker_links:
                    ids = [e["id"] for e in st.session_state.output_json]
                    broker_url = utils.get_entities_broker_link(
                        self.context_cli.broker_url,
                        ids
                    )
                    link = f"[See the entities on the context broker]" \
                           f"({broker_url}) <br/><br/>"
                else:
                    link = ""
                self._st_output_text.markdown(link + "API response:")
                self._st_output_json.write(st.session_state.output_json)
        else:
            self._st_output_text.empty()
            self._st_output_json.empty()

    def _on_predict(self):
        """Call the API to predict the given image and visualize the results.
        """
        try:
            entities = self._call_api_predict(
                st.session_state.input_entity["id"],
                accept=st.session_state.accept_header
            )
            st.session_state.output_json = entities
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"
            return

        if len(entities) == 0:
            return

        try:
            image = self._download_visualize_entities(
                entities,
                st.session_state.visualization_parameters
            )
            st.session_state.output_image = image
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"


    def _on_extract(self):
        pass

    def _on_recognize(self):
        pass

    def _update(self):
        """Handle the UI logic.
        """
        # Get the input entity ID from the text input or the uploaded file
        if st.session_state.uploaded_file is None:
            # Get the entity from the id text input
            if st.session_state.input_id:
                self._set_input_entity_by_id(st.session_state.input_id)
        else:
            # Get the image from the uploaded file
            image_id = self._upload_input_image()
            self._set_input_entity_by_id(image_id)

        self._get_image_from_input()
        self._show_input_image()

        # Set the predict button
        self._st_button_predict.button(
            "Extract features & Recognize",
            type="primary",
            use_container_width=True,
            on_click=self._on_predict,
            disabled=st.session_state.input_image is None
        )
        self._st_button_extract.button(
            "Extract features",
            use_container_width=True,
            on_click=self._on_extract,
            disabled=st.session_state.input_image is None
        )
        self._st_button_recognize.button(
            "Recognize",
            use_container_width=True,
            on_click=self._on_recognize,
            disabled=st.session_state.input_entity is None
        )

        # Clear output if there is no input
        if st.session_state.input_entity is None:
            st.session_state.output_image = None
            st.session_state.output_json = None

        # Show the output image if any
        self._show_output()

        # Show the error message if any
        if st.session_state.error_message is not None:
            self._st_error.error(st.session_state.error_message)
        else:
            self._st_error.empty()
        st.session_state.error_message = None
