import orbitx
import datetime as dt
from dateutil.parser import parse

start = '2024-12-31T23:59:59'
end = '2023-01-01T00:00:00'

start_time = parse(start, fuzzy=False)
end_time = parse(end, fuzzy=False)

matchups=orbitx.return_matchups(["LS8","S2A"],start_time, end_time, 30, 2, 100, 1800)
print(matchups)