from typing import List, Optional, Union

import requests
import streamlit as st

from toolbox.Projects.FrontEnd.utils import utils
from toolbox.utils.utils import urljoin

from . import BaseTemplate


class SimplePredictTemplate(BaseTemplate):
    """Streamlit template for Toolbox Projects which API implements a predict
    method. It allows predicting images by their ID or by uploading them and
    shows the output JSON and image.
    """

    def __init__(self, **kwargs):
        """Create the simple predict Project template.
        """
        super().__init__(**kwargs)

        # Streamlit elements
        self._st_input_image = None
        self._st_preview_image_id = None
        self._st_output_image = None
        self._st_output_json = None
        self._st_output_text = None
        self._st_button_predict = None
        self._st_error = None

        self._upload_mimes = ["png", "jpg", "jpeg", "bmp", "tiff"]

        self.docs_url = urljoin(self.url, "docs")

    def _init_session_state(self):
        """Initialize the session state variables.
        """
        st.session_state.setdefault("error_message", None)
        st.session_state.setdefault("input_image", None)
        st.session_state.setdefault("output_json", None)
        st.session_state.setdefault("output_image", None)
        st.session_state.setdefault("uploaded_file_id", None)
        st.session_state.setdefault("input_entity", None)

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
            st.divider()
            self._st_input_image = st.empty()
            self._st_preview_image_id = st.empty()

        with col_output:
            st.subheader("Output")
            self._st_output_image = st.empty()
            st.divider()
            self._st_output_text = st.empty()
            self._st_output_json = st.empty()

    def _on_predict(self):
        """Call the API to predict the given image and visualize the results.
        """
        try:
            entities = self._call_api(
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
            self._download_visualize_entities(
                entities,
                st.session_state.visualization_parameters
            )
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            st.session_state.error_message = f"Error: {e}"

    def _download_visualize_entities(
        self,
        entities: List[dict],
        visualization_params: dict = {}
    ):
        """Visualize a list of entities by their IDs. Call the image storage
        API to generate the image, then download it.

        Args:
            entities (List[dict]): List of entity dicts to visualize.
            visualization_params (dict, optional): Visualization parameters.
                Defaults to {}.
        """
        entity_ids = [e["id"] for e in entities]
        vis_id = self.image_storage_cli.visualize(
            entity_ids,
            visualization_params=visualization_params)
        st.session_state.output_image = self.image_storage_cli.download(vis_id)

    def _upload_input_image(self) -> Union[str, None]:
        """Upload the input image to the image storage.

        Returns:
            Union[str, None]: The ID of the uploaded image on the image storage
                or None if the upload fails or the image is already uploaded
                to the image storage.
        """
        uploaded_file = st.session_state.uploaded_file
        if st.session_state.uploaded_file_id != uploaded_file.id:
            try:
                image_id = self.image_storage_cli.upload_bytes(
                    image_bytes=uploaded_file.read(),
                    name=uploaded_file.name,
                    file_type=uploaded_file.type,
                    source="toolbox.FrontEnd."+self.name.replace(" ", "_")
                )
                st.session_state.uploaded_file_id = uploaded_file.id
                return image_id
            except Exception as e:
                self.logger.exception(e, exc_info=True)
                st.session_state.error_message = f"Error: {e}"
        return None

    def _set_input_entity_by_id(self, entity_id: str):
        """Get the input entity from the context broker by its ID.

        Args:
            entity_id (str): The ID of the input entity.
        """
        if st.session_state.input_entity is not None and \
                st.session_state.input_entity.get("id", None) == entity_id:
            return
        st.session_state.input_entity = self.context_cli.get_entity(
            entity_id,
            as_dict=True
        )
        if st.session_state.input_entity is None:
            st.session_state.error_message = "Error: Entity " + \
                f"{utils.format_st_id(entity_id)} not found"

    def _get_image_from_input(self):
        """Get the input image from the input entity.
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
        if (st.session_state.input_image is not None and
                st.session_state.input_image.id == image_id):
            return

        # Download the image
        try:
            image = self.image_storage_cli.download(image_id)
            st.session_state.input_image = image
        except:
            st.session_state.error_message = "Error: Image " + \
                utils.format_st_id(image_id) + \
                f" not found on {self.image_storage_cli.url}"

    def _show_input_image(self):
        """Show the input image or entity and its ID caption.
        """
        if st.session_state.input_image is not None:
            self._st_input_image.image(
                st.session_state.input_image.image,
                channels="BGR"
            )
            self._st_preview_image_id.caption(
                utils.format_st_id(st.session_state.input_image.id)
            )
        elif st.session_state.input_entity is not None:
            self._st_input_image.write(st.session_state.input_entity)
            self._st_preview_image_id.caption(
                utils.format_st_id(st.session_state.input_entity["id"])
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
                self._st_output_text.markdown(
                    link + "API response:",
                    unsafe_allow_html=True
                )
                self._st_output_json.write(st.session_state.output_json)
        else:
            self._st_output_text.empty()
            self._st_output_json.empty()

    def _call_api(
        self,
        entity_id: str,
        route: str = "predict",
        post_to_broker: Optional[bool] = None,
        accept: str = "application/json"
    ) -> List[dict]:
        """Call the API.

        Args:
            entity_id (str): ID of the input entity.
            route (str, optional): API route to call. Defaults to "predict".
            post_to_broker (Optional[bool], optional): Post the generated
                entity to the context broker. None to use the API defaults.
                Defaults to None.
            accept (str, optional): Accept header. ``application/json`` or
                ``application/ld+json``. Defaults to "application/json".

        Raises:
            requests.exceptions.HTTPError: If the request fails.

        Returns:
            List[dict]: A list of entities generated by the API.
        """
        route = self.get_api_path(route)
        content = {"entity_id": entity_id}
        if post_to_broker is not None:
            content["post_to_broker"] = post_to_broker
        headers = {"Accept": accept}
        self.logger.info(
            f"Calling {route} with {content} (headers: {headers}))")
        response = requests.post(route, json=content, headers=headers)
        if not response.ok:
            response.raise_for_status()
        return response.json()

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
            "Predict",
            type="primary",
            use_container_width=True,
            on_click=self._on_predict,
            disabled=st.session_state.input_image is None
        )

        # Clear output if there is no input
        if st.session_state.input_entity is None:
            st.session_state.output_image = None
            st.session_state.output_json = None
            st.session_state.input_image = None

        self._show_input_image()

        # Show the output image if any
        self._show_output()

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
