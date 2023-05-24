import streamlit as st
import time
from datetime import timedelta

from timeloop import Timeloop

from toolbox.Projects.FrontEnd.utils import utils

from . import BaseTemplate


class ContextBrokerTemplate(BaseTemplate):

    def __init__(self, **kwargs):
        """Create the context broker template.
        """
        super().__init__(**kwargs)
        self.pagination_limit = kwargs.get("pagination_limit", 100)
        self.server_refresh_rate = kwargs.get("server_refresh_rate", 10) # seconds

        # Context broker metrics (shared among all users)
        self._metrics = {
            "subscriptions_count": 0,
            "entities_count": 0,
            "entity_types": [],
            "entity_type_count": {},
        }
        self._metrics_deltas = {
            "subscriptions_count": 0,
            "entities_count": 0,
            "entity_types": 0,
        }

        # Server metrics loop
        self._time_loop = Timeloop()
        self._time_loop.job(
            interval=timedelta(seconds=self.server_refresh_rate)
        )(self._update_metrics)
        self._time_loop.start()

    def _init_session_state(self):
        """Initialize the session state variables.
        """
        if "error_message" not in st.session_state:
            st.session_state.error_message = None
    
    def _update_metrics(self):
        # Get types
        types = self.context_cli.get_types()
        # Get count per type
        for t in types:
            entities = self.context_cli.get_all_entities(entity_type=t)
            if t not in self._metrics["entity_type_count"]:
                self._metrics["entity_type_count"][t] = 0
            self._metrics["entity_type_count"][t] = len(entities)
        # Get total count
        entities_count = sum(
            self._metrics["entity_type_count"].values()
        )
        # Get subscriptions count
        subscriptions_count = len(
            self.context_cli.get_all_subscriptions()
        )
        
        # Set deltas
        self._metrics_deltas["entities_count"] = (
            entities_count - self._metrics["entities_count"]
        )
        self._metrics_deltas["subscriptions_count"] = (
            subscriptions_count - self._metrics["subscriptions_count"]
        )
        self._metrics_deltas["entity_types"] = (
            len(types) - len(self._metrics["entity_types"])
        )

        # Set metrics
        self._metrics["entity_types"] = types
        self._metrics["subscriptions_count"] = subscriptions_count
        self._metrics["entities_count"] = entities_count

    def _ui_tab_metrics(self):
        cols = st.columns(4)
        with cols[0]:
            st.metric(
                "Subscriptions",
                self._metrics["subscriptions_count"],
                self._metrics_deltas["subscriptions_count"]
            )
        with cols[1]:
            st.metric(
                "Entities",
                self._metrics["entities_count"],
                self._metrics_deltas["entities_count"]
            )
        with cols[2]:
            st.metric(
                "Entity types",
                len(self._metrics["entity_types"]),
                self._metrics_deltas["entity_types"]
            )
        with cols[3]:
            st.table(self._metrics["entity_type_count"])


    def _ui(self):
        """Set the UI elements.
        """
        # Title
        title_info = st.empty()
        if self.description:
            description = self.description + \
                f" The context broker is available on: " +\
                f'<a href="{self.url}">{self.url}</a>'
            utils.write_title_info_toggle(
                self.name,
                description,
                title_info
            )
        else:
            title_info.title(self.name)

        # Error message
        self._st_error = st.empty()

        tab_metrics, a = st.tabs([
            "Real Time Metrics",
            "a"
        ])

        with tab_metrics:
            self._ui_tab_metrics()
        with a:
            st.text("a")

        # with tab_upload:
        #     self._ui_tab_upload()

        # with tab_download:
        #     self._ui_tab_download()

        # with tab_visualization:
        #     self._ui_tab_visualization()

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
