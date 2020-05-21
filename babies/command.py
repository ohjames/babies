import sys
import argparse
import os

from .videos import (
    watch_video,
    create_show_db,
    record_video,
    display_videos,
    grep_show_record,
    enqueue_videos,
    dequeue_videos,
)
from .youtube import search_youtube
from .spotify import search_spotify, listen_to_tracks
from .config import Config


def run_babies():
    parser = argparse.ArgumentParser(description="enjoy your videos")

    paths_help = "paths to videos and/or directories containing series and or/videos"

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    create = subparsers.add_parser(
        "create", help="create series db from shows in a directory", aliases=["c"]
    )
    create.add_argument("paths", help=paths_help, nargs="*")
    create.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force overwrite of existing database",
    )

    find = subparsers.add_parser(
        "find", help="find entry in global record", aliases=["f"]
    )
    find.add_argument(
        "search_terms", help="regular expressions, all must match", nargs="+"
    )
    find.add_argument(
        "-q", "--quiet", action="store_true", help="only show video names"
    )

    watch = subparsers.add_parser(
        "watch",
        help="watch [next] show at each path",
        aliases=["w", "night", "n", "dryrun", "d"],
    )
    watch.add_argument("paths", help=paths_help, nargs="*")
    watch.add_argument(
        "-d",
        "--dont-record",
        action="store_true",
        help="don't write to series or global records",
    )
    watch.add_argument(
        "-n", "--night-mode", action="store_true", help="normalise audio"
    )
    watch.add_argument("-s", "--sub-file", help="subtitle file")
    watch.add_argument("-c", "--comment", help="comment to record with video(s)")
    watch.add_argument("-t", "--title", help="title to record with video(s)")

    enqueue = subparsers.add_parser("enqueue", help="enqueue shows", aliases=["e"])
    enqueue.add_argument("queue_path", help="directory to story queue in")
    enqueue.add_argument("paths", help=paths_help, nargs="+")
    enqueue.add_argument("-c", "--comment", help="comment to record with video(s)")
    enqueue.add_argument("-t", "--title", help="title to record with video(s)")
    enqueue.add_argument(
        "-p",
        "--prune",
        action="store_true",
        help="prune watched videos before queuing next video",
    )

    dequeue = subparsers.add_parser("dequeue", help="dequeue shows", aliases=["de"])
    dequeue.add_argument("queue_path", help="directory with queue")
    dequeue.add_argument("paths", help=paths_help, nargs="+")

    print_cmd = subparsers.add_parser(
        "print", help="display next show at path", aliases=["p"]
    )
    print_cmd.add_argument("paths", help=paths_help, nargs="*")
    print_cmd.add_argument(
        "-i",
        "--ignore-errors",
        action="store_true",
        help="ignore directories with no videos",
    )
    print_cmd.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
    )
    print_cmd.add_argument(
        "-n",
        "--no-extension-filter",
        action="store_true",
        help="do not filter out non-videos",
    )

    path_help = "paths to video and/or directory containing series and or/video"
    record = subparsers.add_parser(
        "record", help="record having watched video", aliases=["r"]
    )
    record.add_argument("path", help=path_help, type=str)
    record.add_argument("comment", help="comment to record with video", type=str)

    search_youtube_cmd = subparsers.add_parser(
        "search_youtube", help="search youtube", aliases=["syt"]
    )
    search_youtube_cmd.add_argument(
        "search_terms", help="youtube search terms", nargs="+"
    )
    search_youtube_cmd.add_argument(
        "-d", "--duration", help="duration (any, long, medium, short)", type=str
    )
    search_youtube_cmd.add_argument(
        "-r", "--raw", help="show raw search results", action="store_true"
    )

    search_spotify_cmd = subparsers.add_parser(
        "search_spotify", help="search spotify", aliases=["ss"]
    )
    search_spotify_cmd.add_argument(
        "search_terms", help="spotify search terms", nargs="+"
    )
    search_spotify_cmd.add_argument(
        "-l", "--limit", help="number of search results to return", type=int
    )
    search_spotify_cmd.add_argument(
        "-r", "--raw", help="show raw search results", action="store_true"
    )

    listen_command = subparsers.add_parser(
        "listen", help="listen to song", aliases=["l"]
    )
    listen_command.add_argument("tracks", help="tracks to listen to", nargs="+")

    argv = sys.argv[1:]
    # if the first argument is a file then prepend the "watch" command
    if len(argv) and "." in argv[0]:
        argv = ["w"] + argv

    args = parser.parse_args(argv)

    paths = []
    try:
        if args.paths:
            paths = args.paths
    except AttributeError:
        pass
    if not paths:
        paths = [os.getcwd()]

    subcommand = args.subcommand
    if subcommand is None:
        watch_video(os.getcwd(), False, False, None, None)
    elif subcommand == "listen" or subcommand == "l":
        listen_to_tracks(args.tracks)
    elif subcommand == "create" or subcommand == "c":
        for path in paths:
            create_show_db(path, args.force)
    elif subcommand == "find" or subcommand == "f":
        grep_show_record(args.search_terms, args.quiet)
    elif subcommand == "record" or subcommand == "r":
        record_video(args.path, args.comment)
    elif subcommand == "enqueue" or subcommand == "e":
        enqueue_videos(
            args.queue_path,
            paths,
            comment=args.comment,
            prune=args.prune,
            title=args.title,
        )
    elif subcommand == "dequeue" or subcommand == "de":
        dequeue_videos(args.queue_path, paths)
    elif subcommand == "print" or subcommand == "p":
        display_videos(
            paths,
            ignore_errors=args.ignore_errors,
            verbose=args.verbose,
            no_extension_filter=args.no_extension_filter,
        )
    elif subcommand == "search_youtube" or subcommand == "syt":
        config = Config()
        search_youtube(config, args.search_terms, duration=args.duration, raw=args.raw)
    elif subcommand == "search_spotify" or subcommand == "ss":
        config = Config()
        search_spotify(config, args.search_terms, limit=args.limit, raw=args.raw)
    else:
        night_mode = subcommand == "night" or subcommand == "n"
        dry_run = subcommand == "dryrun" or subcommand == "d"
        if night_mode or dry_run or subcommand == "watch" or subcommand == "w":
            for path in paths:
                watch_video(
                    path,
                    dry_run or args.dont_record,
                    night_mode or args.night_mode,
                    sub_file=args.sub_file,
                    comment=args.comment,
                    title=args.title,
                )


