import streamlit as st

from . import BaseTemplate

class SimplePredict(BaseTemplate):

    def __init__(self, name: str, port: int, **kwargs):
        super().__init__(name, port, **kwargs)
        self.input_image_id = None
    
    def _on_predict_click(self):
        print("aaaaaaaa")
        
    def __call__(self):
        st.title(self.name)
        col_input, col_output = st.columns(2, gap="large")

        with col_input:
            st.subheader("Input")
            self.input_image_id = st.text_input("Image id")
            st.markdown("<p style='color: gray; text-align: center;'>- or -</p>", unsafe_allow_html=True)
            self.uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg", "bmp", "tiff"],
            )
            st.button("Predict", on_click=self._on_predict_click)
                # with st.spinner('Wait for it...'):
                #     for i in range(int(float(self.input_image_id))):
                #         1+1
                # st.text("Done!")

        with col_output:
            st.subheader("Output")
            st.image("https://via.placeholder.com/800x800", use_column_width=True)
            # if uploaded_file is not None:
            #     st.image(uploaded_file, use_column_width=True)
            #     self.input_image_id = uploaded_file.name


