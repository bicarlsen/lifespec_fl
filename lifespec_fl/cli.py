import os
import argparse
from glob import glob
import logging

import numpy as np
import pandas as pd

from . import parser as fl
from . import data_types


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level = logging.INFO,
            format = '%(message)s'
        )

    files = []
    for p in args.pattern:
        files += glob(p)

    logging.info(f'Matched {files}')

    jdf = []
    for file in files:
        logging.info(f'Converting {file}')
        counts, data = fl.parse(file)

        fn, _ = os.path.splitext(os.path.basename(file))

        df = pd.Series(
            counts[:, 1],
            index = counts[:, 0],
            dtype = int,
            name = 'counts'
        )
        df.index = df.index.rename('time / s')

        if args.convert_time or args.original:
            time_mult = data_types.TimeScale[data['time_scale'][0].value].value
            df.index /= time_mult

            time_scale = data['time_scale'][0].value
            df.index = df.index.rename(f'time / {time_scale}')
            df.index = np.around(df.index, 9)

        if args.original:
            idf = {
                'Labels': data['labels'].value,
                'Type': data['type'].value,
                'Comment': '',
                'Start': '0.00',
                'Stop': f'{data["stop_time"][0].value:0.6f}',
                'Step': data['stop_time'][0].value/(counts.shape[0] - 1),
                'Fixed/Offset': '',
                'XAxis': data['x_axis'][0].value,
                'YAxis': data['y_axis'][0].value
            }

            idf = pd.Series(idf)
            idf = idf.to_frame()
            idf[1] = ''  # empty column to include additional comma as in original
            idf.to_csv(f'{fn}.csv', header = False)

            with open(f'{fn}.csv', 'a') as f:
                f.write('\n')

            df = df.to_frame()
            df['counts'] = df['counts'].apply(lambda x: f'{x:0.8e}')
            df[1] = ''
            df.to_csv(f'{fn}.csv', header = False, mode = 'a')

        elif args.join:
            df = df.rename(fn)
            df = df.reset_index()
            jdf.append(df)

        else:
             df.to_csv(f'{fn}.csv')

    if args.join:
        logging.info('Joining data')
        df = pd.concat(jdf, axis = 1)
        fn = get_new_join_fn()
        df.to_csv( fn, index = False)


def get_parser():
    parser = argparse.ArgumentParser(description = 'Convert .FL file to .csv.')
    parser.add_argument(
        'pattern',
        nargs = '*',
        default = ['*.FL'],
        help = 'Glob pattern(s) to match files for conversion.'
    )

    parser.add_argument(
        '--original',
        action = 'store_true',
        help = 'Save data in the original format as if it was converted to csv by the Lifespec software. If set, this will ignore all other flags.'
    )

    parser.add_argument(
        '--join',
        action = 'store_true',
        help = 'Combine all data into a single file.'
    )

    parser.add_argument(
        '--verbose',
        action = 'store_true',
        help = 'Log actions.'
    )

    parser.add_argument(
        '--convert-time',
        action = 'store_true',
        help = 'Convert time into original time scale.'
    )

    return parser


def get_new_join_fn() -> str:
    """
    :returns: A new file name used for saving joined data.
    """
    def _new_fn(i: int) -> str:
        basename = 'fl_joined_data'
        if i == 0:
            return f'{basename}.csv'

        return f'{basename}-{i}.csv'

    i = 0
    fn = _new_fn(i)
    while os.path.exists(fn):
        i += 1
        fn = _new_fn(i)

    return fn
        
