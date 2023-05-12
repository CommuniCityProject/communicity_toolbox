import argparse
from urllib.parse import quote

import requests

DOUBLE_CONFIRMATION = True
GET_LIMIT = 1000


class ContextBrokerUtils:

    def __init__(self, host: str = "127.0.0.1", port: int = 1026):
        self.url = f"http://{host}:{port}/"
        self._url_types = self.url + "ngsi-ld/v1/types/"
        self._url_entities = self.url + "ngsi-ld/v1/entities/"
        self._url_subscriptions = self.url + "ngsi-ld/v1/subscriptions/"
        self._url_batch_delete = self.url + "ngsi-ld/v1/entityOperations/delete/"

    def _check_response(self, response: requests.models.Response) -> bool:
        if not response.ok:
            print(response.status_code, response.text, response.url)
        return response.ok

    def entities_purge(self):
        # Get types
        r = requests.get(self._url_types)
        if not self._check_response(r):
            return
        types_list = r.json()["typeList"]
        total = 0
        for e_type in types_list:
            while True:
                # Get entities
                r = requests.get(
                    self._url_entities +
                    f"?type={e_type}&limit={GET_LIMIT}"
                )
                # Delete entities
                if not self._check_response(r):
                    break
                entity_ids = [e["id"] for e in r.json()]
                if not entity_ids:
                    break
                total += len(entity_ids)
                r = requests.post(self._url_batch_delete, json=entity_ids)
                if not self._check_response(r):
                    break
        print(f"Total entities deleted: {total}")

    def entity_type_purge(self, e_type: str):
        total = 0
        while True:
            # Get entities
            r = requests.get(
                self._url_entities +
                f"?type={e_type}&limit={GET_LIMIT}"
            )
            # Delete entities
            if not self._check_response(r):
                break
            entity_ids = [e["id"] for e in r.json()]
            if not entity_ids:
                break
            total += len(entity_ids)
            r = requests.post(self._url_batch_delete, json=entity_ids)
            if not self._check_response(r):
                break
        print(f"Total entities deleted: {total}")

    def subscriptions_purge(self):
        total = 0
        while True:
            # Get subscriptions
            r = requests.get(
                self._url_subscriptions +
                f"?limit={GET_LIMIT}"
            )
            if not self._check_response(r):
                break
            subs = r.json()
            if not subs:
                break
            for sub in subs:
                total += 1
                r = requests.delete(
                    self._url_subscriptions +
                    quote(sub["id"])
                )
                if not self._check_response(r):
                    return
        print(f"Total subscriptions deleted: {total}")


class CommandParser:

    def __init__(self):
        # Parse the arguments
        parser = argparse.ArgumentParser()

        # Base parser
        parser.add_argument(
            "--host",
            help="Context broker host (default: '127.0.0.1')",
            default="127.0.0.1"
        )
        parser.add_argument(
            "--port",
            help="Context broker port (default: 1026)",
            type=int,
            default=1026
        )

        # Add sub parsers for each domain
        sub_parser = parser.add_subparsers(
            title="domain",
            dest="domain",
            required=True
        )
        self._add_entities_args(sub_parser)
        self._add_subscriptions_args(sub_parser)

        # Parse args
        args = parser.parse_args()
        self.context_broker_utils = ContextBrokerUtils(args.host, args.port)
        self.host = self.context_broker_utils.url
        print(f"Context broker at {self.host}")

        if args.domain == "entities":
            self._parse_entities_args(args)
        elif args.domain == "subscriptions":
            self._parse_subscriptions_args(args)

    def _add_entities_args(self, sub_parser: argparse.ArgumentParser):
        """Add the entities parser.
        """
        entity_ap = sub_parser.add_parser(
            "entities",
            help="Actions for the entities of the context broker"
        )
        entity_ap.add_argument(
            "--purge",
            action="store_true",
            help="Delete all the entities from the context broker"
        )
        entity_ap.add_argument(
            "--purge-type",
            type=str,
            default=None,
            help="Delete all entities of a certain type from the context broker"
        )
        entity_ap.add_argument(
            "--force",
            action="store_true",
            help="Do not ask for confirmation"
        )

    def _add_subscriptions_args(self, sub_parser: argparse.ArgumentParser):
        """Add the subscriptions parser.
        """
        sub_ap = sub_parser.add_parser(
            "subscriptions",
            help="Actions for the subscriptions of the context broker"
        )
        sub_ap.add_argument(
            "--purge",
            action="store_true",
            help="Delete all the subscriptions from the context broker"
        )
        sub_ap.add_argument(
            "--force",
            action="store_true",
            help="Do not ask for confirmation"
        )

    def _parse_entities_args(self, args: argparse.Namespace):
        if args.purge:
            if not self._confirm_action(
                f"All the entities on the context broker ({self.host})"
                f" will be deleted. Continue?",
                False, not args.force
            ):
                return
            self.context_broker_utils.entities_purge()
        if args.purge_type is not None:
            if not self._confirm_action(
                f"All the {args.purge_type} entities on the context broker "
                f"({self.host}) will be deleted. Continue?",
                False, not args.force
            ):
                return
            self.context_broker_utils.entity_type_purge(args.purge_type)

    def _parse_subscriptions_args(self, args: argparse.Namespace):
        if args.purge:
            if not self._confirm_action(
                f"All the subscriptions on the context broker "
                f"({self.host}) will be deleted. Continue?",
                False, not args.force
            ):
                return
            self.context_broker_utils.subscriptions_purge()

    def _confirm_action(self, message: str, default_option: bool = False,
                        enable: bool = True) -> bool:
        if not enable:
            return True
        conf_options = "[Y/n]" if default_option else "[y/N]"
        confirmation = input(message + " " + conf_options)
        confirmation = confirmation.lower()

        if confirmation not in ["y", "n", ""]:
            return False
        if confirmation == "":
            return default_option
        return confirmation == "y"


if __name__ == "__main__":
    CommandParser()
