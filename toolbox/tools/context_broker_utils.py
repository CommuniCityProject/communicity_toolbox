import argparse
import logging

from toolbox.Context import ContextCli


def confirm_action(message: str, default_option: bool = False,
                   enable: bool = True) -> bool:
    if not enable:
        return True
    conf_options = "[Y/n]" if default_option else "[y/N]"
    confirmation = input(f"{message} {conf_options}")
    confirmation = confirmation.lower()

    if confirmation not in ["y", "n", ""]:
        return False
    if confirmation == "":
        return default_option
    return confirmation == "y"


def parse_entities_args(context_cli: ContextCli, args: argparse.Namespace):
    if args.get_types:
        types = context_cli.get_types()
        print(f"Entity types: {types}")
    if args.count:
        types = context_cli.get_types()
        count = sum([
            len(context_cli.get_all_entities(entity_type=t, as_dict=True))
            for t in types
        ])
        print(f"Total number of entities: {count}")
    if args.count_type is not None:
        count = len(
            context_cli.get_all_entities(
                entity_type=args.count_type,
                as_dict=True
            )
        )
        print(f"Total number of '{args.count_type}' entities: {count}")
    if args.purge:
        types = context_cli.get_types()
        ids = [
            e['id'] for t in context_cli.get_types()
            for e in context_cli.get_all_entities(entity_type=t, as_dict=True)
        ]
        if not confirm_action(
            f"All the entities ({len(ids)}) on the context broker "
            f"{context_cli.broker_url} will be deleted. Continue?",
            False, not args.force
        ):
            return
        [context_cli.delete_entity(e_id) for e_id in ids]
    if args.purge_type is not None:
        ids = [
            e['id']
            for e in context_cli.get_all_entities(
                entity_type=args.purge_type,
                as_dict=True
            )
        ]
        if not confirm_action(
            f"All the '{args.purge_type}' entities ({len(ids)}) on the context "
            f"broker ({context_cli.broker_url}) will be deleted. Continue?",
            False, not args.force
        ):
            return
        [context_cli.delete_entity(e_id) for e_id in ids]
    if args.delete is not None:
        if not confirm_action(
            f"The entity '{args.delete}' will be deleted. Continue?",
            False, not args.force
        ):
            return
        context_cli.delete_entity(args.delete)


def parse_subscriptions_args(context_cli: ContextCli, args: argparse.Namespace):
    if args.count:
        count = len(context_cli.get_all_subscriptions())
        print(f"Total number of subscriptions: {count}")
    if args.delete is not None:
        if not confirm_action(
            f"The subscription '{args.delete}' will be deleted. Continue?",
            False, not args.force
        ):
            return
        context_cli.unsubscribe(args.delete)
    if args.purge:
        ids = [s.subscription_id for s in context_cli.get_all_subscriptions()]
        if not confirm_action(
            f"All the subscriptions ({len(ids)}) on the context broker "
            f"{context_cli.broker_url} will be deleted. Continue?",
            False, not args.force
        ):
            return
        [context_cli.unsubscribe(s_id) for s_id in ids]


def add_entities_args(sub_parser: argparse.ArgumentParser):
    """Add the entities parser.
    """
    entity_ap = sub_parser.add_parser(
        "entities",
        help="Actions for the entities of the context broker"
    )
    entity_ap.add_argument(
        "--get-types",
        action="store_true",
        help="Get the types of the entities on the context broker"
    )
    entity_ap.add_argument(
        "--count",
        action="store_true",
        help="Count the total number of entities on the context broker"
    )
    entity_ap.add_argument(
        "--count-type",
        help="Count the number of entities of a certain type on the "
        "context broker"
    )
    entity_ap.add_argument(
        "--purge",
        action="store_true",
        help="Delete all the entities from the context broker"
    )
    entity_ap.add_argument(
        "--purge-type",
        help="Delete all entities of a certain type from the context broker"
    )
    entity_ap.add_argument(
        "--delete",
        help="Delete one entity from the context broker by its ID"
    )
    entity_ap.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Do not ask for confirmation"
    )


def add_subscriptions_args(sub_parser: argparse.ArgumentParser):
    """Add the subscriptions parser.
    """
    sub_ap = sub_parser.add_parser(
        "subscriptions",
        help="Actions for the subscriptions of the context broker"
    )
    sub_ap.add_argument(
        "--count",
        action="store_true",
        help="Count the total number of subscriptions on the context broker"
    )
    sub_ap.add_argument(
        "--delete",
        help="Delete one subscription from the context broker by its ID"
    )
    sub_ap.add_argument(
        "--purge",
        action="store_true",
        help="Delete all the subscriptions from the context broker"
    )
    sub_ap.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Do not ask for confirmation"
    )


def parse_args():
    # Base parser
    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        "--log-level",
        help="Log level (default: WARNING)",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )

    # Add sub parsers
    sub_parser = parser.add_subparsers(
        title="domain",
        dest="domain",
        required=True
    )
    add_entities_args(sub_parser)
    add_subscriptions_args(sub_parser)

    # Parse args
    args = parser.parse_args()

    logging.getLogger("toolbox").setLevel(args.log_level)
    context_cli = ContextCli(host=args.host, port=args.port)

    if args.domain == "entities":
        parse_entities_args(context_cli, args)
    elif args.domain == "subscriptions":
        parse_subscriptions_args(context_cli, args)


if __name__ == "__main__":
    parse_args()
