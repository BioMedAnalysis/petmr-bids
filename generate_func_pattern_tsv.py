import csv
import argparse


def main(args):
    with open(args.file_name, "wt") as out_file:
        tsv_writer = csv.writer(out_file, delimiter="\t")
        tsv_writer.writerow(["onset", "duration", "trail_type"])

        # add rows
        _time = 0
        tsv_writer.writerow([_time, args.init_onset, args.on_trail])
        _time = _time + args.init_onset

        while True:
            if _time < args.total_duration:
                tsv_writer.writerow(
                    [_time, args.off_duration, args.off_trail],
                )
                _time = _time + args.off_duration
                tsv_writer.writerow([_time, args.on_duration, args.on_trail])
                _time = _time + args.on_duration
            else:
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", help="the output filename")
    parser.add_argument(
        "init_onset", help="the starting onset period in seconds", type=int
    )
    parser.add_argument(
        "off_duration", help="the duration of a single off period", type=int
    )
    parser.add_argument(
        "on_duration", help="the duration of a single onset period", type=int
    )
    parser.add_argument("off_trail", help="offset trail type", type=str)
    parser.add_argument("on_trail", help="onset trail type", type=str)
    parser.add_argument(
        "total_duration", help="total simulation duration in seconds", type=int
    )

    main(parser.parse_args())
