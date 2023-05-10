import numpy as np
import datetime
from operator import add

def get_2LEs(start_time, end_time, sat):



        # region Read TLE file.
        with open('T:/ECO/EOServer/data/satellite_TLEs/TLEset_'+sat+'.txt','r') as f:
                lines = f.readlines()
        lines = np.array(lines)
        # endregion



        # region Access indexes of line-1 and line-2
        length = len(lines)
        if length % 3 == 0:
                number_of_TLEs = int(length / 3)
                line_1_indexes = 3 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 1
                line_2_indexes = 3 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 2
        elif length % 2 == 0:
                number_of_TLEs = int(length / 2)
                line_1_indexes = 3 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 0
                line_2_indexes = 3 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 1
        else:
                print('Error message')
        f = np.vectorize(int)
        line_1_indexes = f(line_1_indexes)
        line_2_indexes = f(line_2_indexes)
        tle_line_1 = lines[line_1_indexes]
        tle_line_2 = lines[line_2_indexes]
        # endregion



        # region Derive datetime
        # Get the year in datetime format
        tens_and_units = [i[18:20] for i in tle_line_1]
        tens_and_units = [int(i) for i in tens_and_units]
        tens_and_units = np.array(tens_and_units)
        year = [datetime.datetime(year = 2000+i ,month=1,day=1) for i in tens_and_units]
        # Get the days_since in timedelta format
        decimal_day = [i[20:32] for i in tle_line_1]
        decimal_day = [float(i) for i in decimal_day]
        decimal_day = np.array(decimal_day)
        days_since_year = [datetime.timedelta(days=i) for i in decimal_day]
        # Get full datetime information
        tle_time = list(map(add, year, days_since_year))
        # endregion



        # region Filter and read relevant lines

        # Get seconds since 2000
        secs_since_2000 = [(i - datetime.datetime(2000,1,1,0,0,0)).total_seconds() for i in tle_time]
        secs_since_2000 = np.array(secs_since_2000)
        start_time_in_secs_since_2000 = (start_time - datetime.datetime(2000,1,1,0,0,0)).total_seconds()
        end_time_in_secs_since_2000 = (end_time - datetime.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()
        # Filter time
        idx_1 = np.array(secs_since_2000 < end_time_in_secs_since_2000)
        idx_2 = np.array(secs_since_2000 > start_time_in_secs_since_2000)
        # idx_3 = This is for an undefined criterion
        idx = idx_1 == idx_2
        # Filter TLE set
        tle_line_1 = tle_line_1[idx]
        tle_line_2 = tle_line_2[idx]
        secs_since_2000 = secs_since_2000[idx]


        return(tle_line_1,tle_line_2,secs_since_2000)