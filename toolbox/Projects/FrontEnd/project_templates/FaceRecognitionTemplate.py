import streamlit as st

from toolbox.Projects.FrontEnd.utils import utils

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

    def _on_extract(self):
        try:
            entities = self._call_api(
                st.session_state.input_entity["id"],
                route="extract",
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
            self._download_visualize_entities(
                entities,
                st.session_state.visualization_parameters
            )
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"

    def _on_recognize(self):
        try:
            entity = self._call_api(
                st.session_state.input_entity["id"],
                route="recognize",
                accept=st.session_state.accept_header
            )
            st.session_state.output_json = [entity]
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"
            return

        try:
            self._download_visualize_entities(
                [entity],
                st.session_state.visualization_parameters
            )
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"

    def _update(self):
        """Handle the UI logic.
        """
        # Get the input entity ID from the text input or the uploaded file
        if st.session_state.uploaded_file is None:
            if st.session_state.input_id:
                # Get the entity from the id text input
                self._set_input_entity_by_id(
                    utils.format_input_id(st.session_state.input_id)
                )
            else:
                # Clear the input entity
                st.session_state.input_entity = None
        else:
            # Get the image from the uploaded file
            image_id = self._upload_input_image()
            if image_id is not None:
                self._set_input_entity_by_id(image_id)

        self._get_image_from_input()

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

        print(st.session_state.output_image)

        # Clear output if there is no input
        if st.session_state.input_entity is None:
            st.session_state.output_image = None
            st.session_state.output_json = None

        # Show the inout image if any
        self._show_input_image()

        # Show the output image if any
        self._show_output()

        # Show the error message if any
        if st.session_state.error_message is not None:
            self._st_error.error(st.session_state.error_message)
        else:
            self._st_error.empty()
        st.session_state.error_message = None
