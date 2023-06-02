from datetime import timedelta

import pandas
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from timeloop import Timeloop

from toolbox.Projects.FrontEnd.utils import utils

from . import BaseTemplate


class ContextBrokerTemplate(BaseTemplate):

    def __init__(self, **kwargs):
        """Create the context broker template.
        """
        super().__init__(**kwargs)
        self.pagination_limit = kwargs.get("pagination_limit", 100)
        self.refresh_rate = kwargs.get("refresh_rate", 10)  # seconds
        assert self.refresh_rate >= 1, "Refresh rate must be >= 1s"

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
        self._update_metrics()
        self._time_loop = Timeloop()
        self._time_loop.job(
            interval=timedelta(seconds=self.refresh_rate)
        )(self._update_metrics)
        self._time_loop.start()

    def _init_session_state(self):
        """Initialize the session state variables.
        """
        st.session_state.setdefault("error_message", None)
        st.session_state.setdefault("subscriptions", None)
        st.session_state.setdefault("entity_types", None)
        st.session_state.setdefault("entities", None)

    def _update_metrics(self):
        """Update the context broker metrics.
        """
        # Get types
        types = self.context_cli.get_types()
        # Get count per type
        for t in types:
            entities = self.context_cli.get_all_entities(
                entity_type=t,
                as_dict=True
            )
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
        """Show context broker real time metrics.
        """
        # Run the client auto refresh loop
        st_autorefresh(
            interval=self.refresh_rate * 1000,
            key="metrics_update"
        )

        cols = st.columns(3, gap="small")
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
        st.divider()
        st.subheader("Entity types")
        pd = pandas.DataFrame(
            self._metrics["entity_type_count"].values(),
            index=self._metrics["entity_type_count"].keys(),
            columns=["Count"],

        )
        st.experimental_data_editor(
            pd,
            use_container_width=True,
            disabled=True
        )

    def _get_subscriptions(self):
        st.session_state.subscriptions = list(
            self.context_cli.iterate_subscriptions(
                limit=self.pagination_limit,
            )
        )

    def _ui_tab_subscriptions(self):
        # Get the subscriptions
        if st.session_state.subscriptions is None:
            self._get_subscriptions()

        # Refresh and search
        col_refresh, col_search = st.columns(2, gap="small")
        with col_refresh:
            st.button(
                "Refresh",
                on_click=self._get_subscriptions,
                key="refresh_subscriptions"
            )
        with col_search:
            id_search = st.text_input(
                "Search",
                placeholder="Search",
                label_visibility="collapsed",
                key="text_input_subscriptions_search"
            )
            id_search = utils.format_input_id(id_search)

        # Render pages
        if id_search:
            # Show a single subscription
            try:
                subscription = self.context_cli.get_subscription(id_search)
                if subscription is not None:
                    if self.context_broker_links:
                        url = utils.get_subscription_broker_link(
                            self.context_cli.broker_url,
                            subscription.subscription_id
                        )
                        st.markdown(
                            f"[See it in the Context Broker]({url})",
                        )
                    st.write(subscription.json)
                else:
                    st.warning("Subscription not found")
            except Exception as e:
                st.session_state.error_message = str(e)
        else:
            # Show all subscriptions
            page = st.session_state.subscriptions_page \
                if "subscriptions_page" in st.session_state else 1
            if st.session_state.subscriptions:
                for sub in st.session_state.subscriptions[page - 1]:
                    parsed_id = utils.format_st_id(sub.subscription_id)
                    with st.expander(parsed_id):
                        if self.context_broker_links:
                            url = utils.get_subscription_broker_link(
                                self.context_cli.broker_url,
                                sub.subscription_id
                            )
                            st.markdown(
                                f"[See it in the Context Broker]({url})"
                            )
                        st.write(sub.json)
                # Page selector
                st.number_input(
                    "Page",
                    min_value=1,
                    max_value=max(len(st.session_state.subscriptions), 1),
                    value=1,
                    key="subscriptions_page",
                )
            else:
                st.caption("No subscriptions found")

    def _get_entity_types(self):
        st.session_state.entity_types = self.context_cli.get_types()
    
    def _get_entities(self):
        if not st.session_state.selected_types:
            st.session_state.entities = []
        else:
            st.session_state.entities = list(
                self.context_cli.iterate_entities(
                    entity_type=st.session_state.selected_types,
                    limit=self.pagination_limit,
                    order_by="!dateModified,!dateCreated,!dateObserved",
                    as_dict=True
                )
            )

    def _ui_tab_entities(self):
        # Get the entity types
        if st.session_state.entity_types is None:
            self._get_entity_types()
        
        # Types selector
        st.multiselect(
            "Entity type",
            options=st.session_state.entity_types,
            default=st.session_state.entity_types,
            key="selected_types",
            on_change=self._get_entities
        )
        
        # Get the entities from the selected types
        if st.session_state.entities is None:
            self._get_entities()

        # Refresh and search
        col_refresh, col_search = st.columns(2, gap="small")
        with col_refresh:
            st.button(
                "Refresh",
                on_click=self._get_entities,
                key="refresh_entities"
            )
        with col_search:
            id_search = st.text_input(
                "Search",
                placeholder="Search",
                label_visibility="collapsed",
                key="text_input_entities_search"
            )
            id_search = utils.format_input_id(id_search)

        # Render pages
        if id_search:
            # Show a single entity
            try:
                entity = self.context_cli.get_entity(id_search, as_dict=True)
                if entity is not None:
                    if self.context_broker_links:
                        url = utils.get_entities_broker_link(
                            self.context_cli.broker_url,
                            entity["id"]
                        )
                        st.markdown(
                            f"[See it in the Context Broker]({url})",
                        )
                    st.write(entity)
                else:
                    st.warning("Entity not found")
            except Exception as e:
                st.session_state.error_message = str(e)
        else:
            # Show all entities from the selected types
            page = st.session_state.entities_page \
                if "entities_page" in st.session_state else 1
            if st.session_state.entities:
                for ent in st.session_state.entities[page - 1]:
                    parsed_id = utils.format_st_id(ent["id"])
                    with st.expander(parsed_id):
                        if self.context_broker_links:
                            url = utils.get_entities_broker_link(
                                self.context_cli.broker_url,
                                ent["id"]
                            )
                            st.markdown(
                                f"[See it in the Context Broker]({url})"
                            )
                        st.write(ent)
                # Page selector
                st.number_input(
                    "Page",
                    min_value=1,
                    max_value=max(len(st.session_state.entities), 1),
                    value=1,
                    key="entities_page",
                )
            else:
                st.caption("No entities found")

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

        tab_metrics, tab_subscriptions, tab_entities = st.tabs([
            "Real Time Metrics",
            "Subscriptions",
            "Entities",
        ])

        with tab_metrics:
            self._ui_tab_metrics()

        with tab_subscriptions:
            self._ui_tab_subscriptions()

        with tab_entities:
            self._ui_tab_entities()

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
