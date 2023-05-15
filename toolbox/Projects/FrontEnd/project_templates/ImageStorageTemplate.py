import streamlit as st
import requests

from . import BaseTemplate


class ImageStorageTemplate(BaseTemplate):

    def __init__(self, **kwargs):
        """Create the SimplePredict Project template.
        """
        super().__init__(**kwargs)

        # Streamlit elements
    
    def _init_session_state(self):
        """Initialize the session state variables.
        """
        pass

    def _ui(self):
        """Set the UI elements.
        """
        st.title(self.name)
        self._st_error = st.empty()

        r = requests.get("http://127.0.0.1:1026/ngsi-ld/v1/entities?type=Image&limit=3&offset=0")
        for ent in r.json():
            parsed_id = ent['id'].replace(":", "\:")
            with st.expander(parsed_id):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(f"http://127.0.0.1:9001/{ent['id']}", channels="BGR")
                with col2:
                    st.write(ent)
                
    def _update(self):
        """Handle the UI logic.
        """
        pass

    def __call__(self):
        self._init_session_state()
        self._ui()
        self._update()
