import pandas as pd

xmas = pd.DataFrame({'holiday': 'christmas',
                     'ds': pd.to_datetime(['2022-12-25', '2023-12-25', '2024-12-25' , '2025-12-25']),
                    'lower_window': -2,
                    'upper_window': 0})

nye = pd.DataFrame({'holiday': 'new_years',
                    'ds': pd.to_datetime(['2022-12-31', '2023-12-31', '2024-12-31']),
                    'lower_window': -2,
                    'upper_window': 0})

easter = pd.DataFrame({'holiday': 'easter',
                       'ds': pd.to_datetime(['2022-01-17', '2023-04-09', '2024-03-31', '2025-04-20']),
                       'lower_window': -2,
                       'upper_window': 0})

fourth_of_july = pd.DataFrame({'holiday': 'forth_of_july',
                               'ds': pd.to_datetime(['2022-06-04', '2023-07-04', '2024-07-04', '2025-07-04']),
                               'lower_window': -3,
                               'upper_window': 2})

superbowl = pd.DataFrame({'holiday': 'superbowl', 
                          'ds': pd.to_datetime(['2022-02-13', '2023-02-12', '2024-02-11', '2025-02-09' ]),
                          'lower_window': -4,
                          'upper_window': 0})

college_football = pd.DataFrame({'holiday': 'college_football', 
                                 'ds': pd.to_datetime(['2022-01-10', '2023-01-09', '2024-01-08', '2025-01-20']),
                                 'lower_window': -2,
                                 'upper_window': 0})

thanksgiving = pd.DataFrame({'holiday': 'thanksgiving', 
                                 'ds': pd.to_datetime(['2022-01-10', '2023-01-09', '2024-01-08', '2025-01-20']),
                                 'lower_window': -2,
                                 'upper_window': 0})

memorial_day = pd.DataFrame({'holiday': 'memorial_day', 
                                 'ds': pd.to_datetime(['2022-05-30', '2023-05-29', '2024-05-27', '2025-05-26']),
                                 'lower_window': -2,
                                 'upper_window': 0})
labor_day = pd.DataFrame({'holiday': 'labor_day', 
                                 'ds': pd.to_datetime(['2022-09-05', '2023-09-04', '2024-09-02', '2025-09-01']),
                                 'lower_window': -2,
                                 'upper_window': 0})

halloween = pd.DataFrame({'holiday': 'halloween', 
                                 'ds': pd.to_datetime(['2022-10-31', '2023-10-31', '2024-10-31', '2025-10-31']),
                                 'lower_window': -2,
                                 'upper_window': 0})
# march_madness ??? too many dates

xtra = pd.DataFrame({'holiday': 'halloween', 
                                 'ds': pd.to_datetime(['2022-12-21']),
                                 'lower_window': -2,
                                 'upper_window': 0})

# combine all the holidays into one dataset
holidays = pd.concat([xmas, nye, easter, fourth_of_july, superbowl, college_football, thanksgiving, memorial_day, labor_day, halloween, xtra])