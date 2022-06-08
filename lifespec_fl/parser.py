import pkg_resources
import struct
import numpy as np
import typing
import yaml
import parse_binary_file as pbf

from .data_types import TimeScale


class FlParser(pbf.Parser):
    def __init__(self):
        desc = load_fl_description()
        info = desc['info'] if ('info' in desc) else None
        defaults = (
            desc['default_options']
            if ('default_options' in desc) else
            None
        )

        format = pbf.FileFormat.from_dicts(
            desc['fields'],
            info=info,
            defaults=defaults
        )

        super().__init__(format)


def parse(file: str) -> typing.Tuple[np.ndarray, pbf.Data]:
    """
    Parse a .FL file.

    :param file: Path to a `.FL` file.
    :returns tuple[numpy.ndarray, parse_binary_file.Data]: Tuple of (counts, data) where
        `counts` is an (channels x 2) array with the first element of each row
        being the time bin and the second being the counts.
        `data` is the parse_binary_file.Data object representing the parsed file.
    """
    parser = FlParser()
    with open(file, 'rb') as f:
        data = parser.parse(f)

    data_buffer_head = data['data_buffer_head'].value
    if data_buffer_head == b'\x30':
        cnt_offset = 1

    elif data_buffer_head == b'\x31':
        data_buffer = data['data'].value[:2]
        if data_buffer == b'\x2e\x39':
            cnt_offset = 3

        elif data_buffer == b'\x39\x2e':
            cnt_offset = 4

        else:
            raise ValueError(f'Unknown data buffer value {data_buffer:02X}')

    else:
        raise ValueError(f'Unknown data buffer head value {data_buffer_head:02X}')

    counts = data['data'].value[cnt_offset:]
    field_size = pbf.data_types.DataSize.FLOAT.value
    n_counts = len(counts)/ field_size
    if n_counts != int(n_counts):
        raise ValueError('Invalid data length.')

    n_counts = int(n_counts)
    counts = [
        struct.unpack('<f', counts[i*field_size:(i+1)*field_size])[0]
        for i in range(n_counts)
    ]

    # `time_scale` and `stop_time` both have 2 entries
    # ensure they match
    time_scale = data['time_scale']
    if time_scale[0].value != time_scale[1].value:
        raise ValueError(f'Found differing time scales ({time_scale[0].value}, {time_scale[1].value})')

    time_scale = time_scale[0].value

    stop_time = data['stop_time']
    if stop_time[0].value != stop_time[1].value:
        raise ValueError(f'Found differing stop times ({stop_time[0].value}, {stop_time[1].value})')

    stop_time = stop_time[0].value

    # calculate times in seconds
    time_mult = TimeScale[time_scale].value
    times = np.linspace(0, stop_time, num=n_counts) * time_mult

    counts = np.column_stack((times, np.array(counts)))

    return (counts, data)


def load_fl_description() -> dict:
    """
    Returns a dictionary describing the .FL file format
    for us with the `parse_binary_file` package.

    :returns dict:
    """
    file = pkg_resources.resource_filename(
        'lifespec_fl',
        'data/fl_descriptor.yaml'
    )

    with open(file) as f:
        desc = yaml.safe_load(f)

    return desc
