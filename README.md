# Lifespec FL

Parse `.FL` files from a Lifespec TRPL machine.

> Install with `python -m pip install lifespec-fl`

## Parser
The `lifespec_fl.parse(<file>)` method is used to parse a .FL file.
This is the main function of this package.

### File format description
Parsing the .FL binary file uses the [`parse_binary_file`](https://pypi.org/project/parse-binary-file/) package. This package uses configuration files to describe the structure of a binary file format for parsing.

You can find this configuration file at `lifespec_fl/data/fl_descriptor.yaml`.

## CLI
Installs a command line interface (CLI) named `lifespec_fl` that can be used to
convert .FL files to .csv.

## Example

### Library
```python
import pandas as pd
import lifespec_fl as fl


# parse the 'my_trpl.FL' file
(counts, data) = fl.parse('my_trpl.FL')

# place counts into a pandas Series
df = pd.Series(counts[:, 1], index = counts[:, 0])
```

### CLI
Convert all .FL files in the current directory to .csv.
```bash
lifespec_fl
```

Convert all .FL files ending in `trpl` in the current directly into a single .csv.
```bash
lifespec_fl --join *trpl.FL
```

# File Format Notes
+ 3 lines separated by `\r\n` (`0d0a`)
+ Little Endian
+ `latin-1` encoded
+ Heads of lines 1 and 2 follow similar pattern

### Line 0 (0x00 - 0x14, 0x15 bytes)
`EAI Multiple Scans` null terminated (`0x00`) string followed by `\r\n`

### Line 1 (0x15 - 0x60, 0x4d bytes)
**head (0x34 bytes)**

0. bytes 0x00 - 0x01 (0x02 bytes): `dc05`
1. bytes 0x02 - 0x05 (0x04 bytes): `0000 0033`
2. bytes 0x06 - 0x09 (0x04 bytes): `0000 0096`
3. bytes 0x0a - 0x10 (0x07 bytes): null
4. bytes 0x11 - 0x14 (0x04 bytes): Stop time as a float
5. bytes 0x15 - 0x19 (0x05 bytes): X axis label (e.g. `'Time'`) as a null terminated string
6. bytes 0x1a - 0x1c (0x03 bytes): Time scale (e.g. `'ns'`, `'us'`) as a null terminated string
7. bytes 0x1d - 0x20 (0x04 bytes): null
8. bytes 0x21 - 0x24 (0x04 bytes): ?, possibly no. of counts in 1000 as float
9. bytes 0x25 - 0x2b (0x07 bytes): Y axis label (e.g. `'Counts'`) as a null terminated string
10. bytes 0x2c - 0x33 (0x08 bytes): `'1.4.5.0'` null terminated string, version?

**body**

11. bytes 0x36 - 0x3d (0x08 bytes): Seems to always be `6400 0000 0100 0000`
12. bytes 0x3e - 0x4c (0x0d bytes): Scan type as null terminated string
13. bytes 0x4d - 0x4e (0x02 bytes): `\r\n` to end line

### Line 2 (0x61 - end)
**head (0x34 bytes)**

0. bytes 0x00 - 0x01 (0x02 bytes): `8813`
1. bytes 0x02 - 0x06 (0x04 bytes): ?, float
2. bytes 0x07 - 0x09 (0x04 bytes): `0100 0096`, control sequence?
3. bytes 0x0a - 0x10 (0x07 bytes): null
4. bytes 0x11 - 0x14 (0x04 bytes): Stop time as a float
5. bytes 0x15 - 0x19 (0x05 bytes): X axis label (e.g. `'Time'`) as a null terminated string
6. bytes 0x1a - 0x1c (0x03 bytes): Time scale (e.g. `'ns'`, `'us'`) as a null terminated string
7. bytes 0x1d - 0x24 (0x08 bytes): null
9. bytes 0x25 - 0x2b (0x07 bytes): Y axis label (e.g. `'Counts'`) null terminated string
10. bytes 0x2c - 0x33 (0x08 bytes): `'1.4.5.0'` null terminated string, version?

**body**

11. Original file name, null terminated
12. (0x01 bytes) `2c`
13. (0x04 bytes) `0100 0000`, control secquence? 
14. (0x02 bytes) `0400`
15. (0x02 bytes) null
16. (0x0f bytes) ?
17. (0x02 bytes) `4090`, control sequence?
18. (0x04 bytes) `0100 0000`, control sequence?
19. (0x04 bytes) ?, null terminated
20. (0x07 bytes) null
21. (0x04 bytes) `f401 0000`, control sequence?
22. (0x0c bytes) `'TCSPC Diode'` string, null terminated
23. (0x0a bytes) null
24. (0x0a bytes) `'Reference'` string, null terminated
25. (0x02 bytes) null
26. (0x03 bytes) `'HC'` string, null terminated
27. (0x04 bytes) `f6ff ffff`, control sequence?
28. (0x02 bytes) `1000`
29. (0x03 bytes) null
30. (0x02 bytes) `000c`
31. (0x0c bytes) `'TCSPC Diode'` sting, null t2rminated
32. (0x06 bytes) null
33. (0x01 bytes) `fe`, control sequence?
34. (0x04 bytes) `'K B'` string, null terminated
35. (0x01 bytes) null
36. (0x0a bytes) `'HS PMT920'` string, null terminated
37. (0x05 bytes) ?, float
38. (0x06 bytes) `00f6 ffff ff0d 00` control sequence?
39. (0x03 bytes) null
40. (0x0d bytes) `'200nm-1000nm'` string, null terminated
41. (0x01 bytes) `05`, control sequence?
42. (0x12 bytes) `'High Speed PMT920'` string, null terminated
43. (0x02 bytes) `0001`
44. (0x16 bytes) null
45. `002c 0100 0001 0000 00` control sequence?
46. (0x04 bytes) ?, float?
47. (0x04 bytes) ?, float?
48. (0x0d bytes) `c220 b043 2000 0000`
49. Time scale string (e.g. `'50ns'`, `'100ns'`), null terminated
50. (0x01 bytes) Data padding
    + If `30`, skip next byte
    + If `31`
        + If `2e39`, skip next byte
        + if `392e`, skip next 2 bytes

**data**
+ Each 4 bytes should be interpreted as a float
