import streamlit as st
import requests

from toolbox.Structures import Image

from . import BaseTemplate


class SimplePredict(BaseTemplate):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Streamlit widgets
        self._st_input_image = None
        self._st_image_id = None
        self._st_output_image = None
        self._st_output_json = None
        self._st_button_predict = None
        
        self._input_image_id = None
        self._uploaded_file = None
        self._output_json = None

    def _call_api_predict(self, image_id: str):
        response = requests.post(
            self.get_api_path("predict"),
            json={"entity_id": image_id}
        )
        if response.ok:
            self._output_json = response.json()


    def _set_input_image(self, image_id: str):
        """Set the input image and update the UI.

        Args:
            image_id (str): ID of the image on the image storage.
        """
        parsed_id = image_id.replace(":", "\:")
        try:
            image = self.image_storage_cli.download(image_id)
            self._st_input_image.image(image.image, channels="BGR")
            self._st_image_id = st.caption(f"ID: {parsed_id}")
        except:
            self._st_input_image.error(
                f"Error: Image '{parsed_id}' not found on "
                f"{self.image_storage_cli.url}"
            )

    def _upload_image(self, st_uploaded_file):
        """Uploads an image previously uploaded to the Streamlit app to the
        image storage and updates the UI.

        Args:
            st_uploaded_file (streamlit.uploaded_file_manager.UploadedFile): 
                Image uploaded to the Streamlit app.
        """
        try:
            image_id = self.image_storage_cli.upload_bytes(
                image_bytes=st_uploaded_file.read(),
                name=st_uploaded_file.name,
                file_type=st_uploaded_file.type,
                source="toolbox.FrontEnd",
            )
        except Exception as e:
            self._st_input_image.error(f"Error: {str(e)}")
        else:
            self._input_image_id = image_id
            self._set_input_image(image_id)

    def _ui(self):
        st.title(self.name)
        col_input, col_output = st.columns(2, gap="large")

        with col_input:
            st.subheader("Input")
            self._input_image_id = st.text_input("Image ID", )
            st.write(
                "<p style='color: gray; text-align: center;'>- or -</p>",
                unsafe_allow_html=True
            )
            self._uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg", "bmp", "tiff"],
            )
            st.write("</br>", unsafe_allow_html=True)
            self._st_button_predict = st.empty()
            st.divider()
            self._st_input_image = st.empty()
            self._st_image_id = st.empty()

        with col_output:
            st.subheader("Output")
            self._st_output_image = st.empty()
            self._st_output_json = st.empty()

    def _update(self):
        button_predict_enabled = True

        if self._uploaded_file is not None:
            self._upload_image(self._uploaded_file)
        elif self._input_image_id is not None and self._input_image_id != "":
            self._set_input_image(self._input_image_id)
        else:
            button_predict_enabled = False
    
        if st.button(
            "Predict",
            on_click=lambda: 1+1,
            disabled=not button_predict_enabled
        ):
            pass


        

    def __call__(self):
        self._ui()
        self._update()
